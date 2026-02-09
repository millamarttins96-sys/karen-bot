# -*- coding: utf-8 -*-
"""
MONITOR GMAIL - Detecta emails do Notion REAIS
"""

import imaplib
import email
from email.header import decode_header
import config
import re

class GmailMonitor:
    def __init__(self):
        self.email = config.GMAIL_EMAIL
        self.password = config.GMAIL_PASSWORD
        self.imap = None
        
    def connect(self):
        try:
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com")
            self.imap.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"Erro Gmail: {e}")
            return False
    
    def get_notion_emails(self):
        """Busca emails NOVOS do Notion"""
        if not self.imap:
            if not self.connect():
                return []
        
        try:
            self.imap.select("INBOX")
            status, messages = self.imap.search(None, '(UNSEEN FROM "notify@notion.so")')
            
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            demandas = []
            
            for email_id in email_ids[-5:]:  # Últimos 5
                status, msg_data = self.imap.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode(errors='ignore')
                
                demanda = self._parse_email(subject, body)
                if demanda:
                    demandas.append(demanda)
            
            return demandas
        except Exception as e:
            print(f"Erro ao buscar emails: {e}")
            return []
    
    def _parse_email(self, subject, body):
        """Extrai informações do email"""
        try:
            # Procurar link Notion
            notion_link = None
            for line in body.split('\n'):
                if 'notion.so' in line and 'http' in line:
                    match = re.search(r'https://[^\s]+notion\.so[^\s]+', line)
                    if match:
                        notion_link = match.group(0)
                        break
            
            # Tentar identificar cliente
            cliente = "Desconhecido"
            
            # Lista de clientes conhecidos
            clientes_conhecidos = [
                "Araceli", "Carina", "Nicole", "Daniel Breia", "Equestre", 
                "Fabi", "Maria Clara", "Pop Decor", "Biomagistral", 
                "Carol Galvão", "Fabrício", "Gabriela", "Lar & Estilo",
                "Priscila", "Karen Ferreira", "Ariella", "Mariana"
            ]
            
            texto_completo = (subject + " " + body).lower()
            for nome in clientes_conhecidos:
                if nome.lower() in texto_completo:
                    cliente = nome
                    break
            
            return {
                'assunto': subject,
                'link': notion_link,
                'cliente': cliente,
                'corpo': body[:300],
                'tipo': 'design'
            }
        except Exception as e:
            print(f"Erro ao parsear: {e}")
            return None

gmail = GmailMonitor()
