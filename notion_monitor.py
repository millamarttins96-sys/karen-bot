import imaplib
import email
from email.header import decode_header
import os
import time
import threading
from dotenv import load_dotenv
from handlers import send_new_demand, send_alteration  # Importe suas funções de envio de notificação do Telegram

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def parse_notion_email(raw_email):
    # Parseia o email cru
    msg = email.message_from_bytes(raw_email)
    subject = decode_header(msg['Subject'])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()

    # Pega o corpo do email (assume texto plano ou HTML simples)
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    # Parseia o corpo baseado na estrutura do PDF (ajuste se o email do Notion for diferente)
    lines = body.split('\n')
    data = {'client': '', 'demanda': '', 'copy': '', 'link': '', 'is_alteration': False}
    in_copy = False
    for line in lines:
        line = line.strip()
        if 'alteração' in line.lower() or 'correção' in line.lower():
            data['is_alteration'] = True
        if line.startswith('Cliente:'):
            data['client'] = line.split(':', 1)[1].strip()
        elif line.startswith('Demanda:'):
            data['demanda'] = line.split(':', 1)[1].strip()
        elif line.startswith('Copy completa:'):
            in_copy = True
            continue
        elif line.startswith('Link:') or 'notion.so' in line:
            data['link'] = line.split(':', 1)[1].strip() if ':' in line else line
        elif in_copy:
            if data['copy']:
                data['copy'] += '\n'
            data['copy'] += line

    # Se for alteração, ajuste campos (ex: "O que mudou" em vez de copy)
    if data['is_alteration']:
        data['copy'] = 'Alteração: ' + data['copy']  # Ajuste conforme necessário

    return data

def poll_email_for_notion(bot):
    while True:
        try:
            # Conecta ao IMAP (Gmail)
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            mail.select('inbox')

            # Busca emails não lidos do Notion
            status, messages = mail.search(None, '(UNSEEN FROM "notifier@notion.so")')
            messages = messages[0].split(b' ')

            for num in messages:
                if not num:
                    continue
                _, msg = mail.fetch(num, '(RFC822)')
                data = parse_notion_email(msg[0][1])

                if data['client'] and data['demanda']:  # Valida se parseou bem
                    if data['is_alteration']:
                        send_alteration(bot, TELEGRAM_CHAT_ID, data)  # Envia notificação de alteração
                    else:
                        send_new_demand(bot, TELEGRAM_CHAT_ID, data)  # Envia notificação de nova demanda
                    # Marca como lido
                    mail.store(num, '+FLAGS', '\\Seen')

            mail.close()
            mail.logout()
        except Exception as e:
            print(f"Erro no polling de email: {e}")

        time.sleep(300)  # Checa a cada 5 minutos

def start_notion_polling(bot):
    thread = threading.Thread(target=poll_email_for_notion, args=(bot,))
    thread.daemon = True
    thread.start()
