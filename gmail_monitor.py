# -*- coding: utf-8 -*-
"""
Monitor de Gmail - Detecta emails do Notion
"""

import imaplib
import email
from email.header import decode_header
import config

class GmailMonitor:
    """Monitora Gmail para notificações do Notion"""
    
    def __init__(self):
        self.email = config.GMAIL_EMAIL
        self.password = config.GMAIL_PASSWORD
        self.imap = None
        
    def connect(self):
        """Conecta ao Gmail"""
        try:
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com")
            self.imap.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"Erro ao conectar Gmail: {e}")
            return False
    
    def get_notion_emails(self, unseen_only=True):
        """Busca emails do Notion"""
        if not self.imap:
            if not self.connect():
                return []
        
        try:
            self.imap.select("INBOX")
            
            # Buscar emails do Notion
            search_criteria = '(FROM "notify@notion.so")'
            if unseen_only:
                search_criteria = '(UNSEEN FROM "notify@notion.so")'
            
            status, messages = self.imap.search(None, search_criteria)
            
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            emails_data = []
            
            for email_id in email_ids[-10:]:  # Últimos 10
                status, msg_data = self.imap.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Decodificar subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                # Pegar corpo do email
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                # Extrair informações
                demanda = self._parse_notion_email(subject, body)
                if demanda:
                    emails_data.append(demanda)
            
            return emails_data
            
        except Exception as e:
            print(f"Erro ao buscar emails: {e}")
            return []
    
    def _parse_notion_email(self, subject, body):
        """Extrai dados do email do Notion"""
        try:
            # Procurar por link do Notion
            notion_link = None
            for line in body.split('\n'):
                if 'notion.so' in line:
                    notion_link = line.strip()
                    break
            
            # Identificar cliente e demanda
            demanda = {
                'assunto': subject,
                'link': notion_link,
                'corpo': body[:500],  # Primeiros 500 chars
                'cliente': 'Desconhecido',
                'tipo': 'design',
                'timestamp': config.get_now()
            }
            
            # Tentar identificar cliente pelo subject ou body
            for cliente in ['Araceli', 'Carina', 'Carol', 'Priscila', 'Gabriela', 
                          'Fabi', 'Daniel', 'Equestre', 'Biomagistral']:
                if cliente.lower() in subject.lower() or cliente.lower() in body.lower():
                    demanda['cliente'] = cliente
                    break
            
            return demanda
            
        except Exception as e:
            print(f"Erro ao parsear email: {e}")
            return None
    
    def mark_as_read(self, email_id):
        """Marca email como lido"""
        try:
            self.imap.store(email_id, '+FLAGS', '\\Seen')
            return True
        except:
            return False
    
    def disconnect(self):
        """Desconecta do Gmail"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

# Instância global
gmail_monitor = GmailMonitor()
