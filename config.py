# -*- coding: utf-8 -*-
"""
KAREN BOT - Configurações Completas
Todas as credenciais e configurações em um lugar
"""

import os
from datetime import datetime, timezone, timedelta

# =====================================================
# FUSO HORÁRIO BRASIL
# =====================================================

BRASILIA_TZ = timezone(timedelta(hours=-3))

def get_now():
    """Retorna datetime atual em Brasília"""
    return datetime.now(BRASILIA_TZ)

def get_data_atual():
    """Retorna data formatada"""
    return get_now().strftime("%d/%m/%Y")

def get_hora_atual():
    """Retorna hora formatada"""
    return get_now().strftime("%H:%M")

def get_dia_semana():
    """Retorna dia da semana em português"""
    dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    return dias[get_now().weekday()]

def get_semana_atual():
    """Retorna datas da semana atual (segunda a sexta)"""
    hoje = get_now()
    dia_semana = hoje.weekday()  # 0=segunda, 6=domingo
    
    # Calcular segunda-feira desta semana
    dias_ate_segunda = dia_semana
    segunda = hoje - timedelta(days=dias_ate_segunda)
    
    # Se hoje é sábado ou domingo, pegar próxima semana
    if dia_semana >= 5:
        segunda = segunda + timedelta(days=7)
    
    semana = []
    dias_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    for i in range(5):
        dia = segunda + timedelta(days=i)
        semana.append({
            "nome": dias_nome[i],
            "data": dia.strftime("%d/%m"),
            "data_completa": dia.strftime("%d/%m/%Y"),
            "objeto": dia
        })
    
    return semana

def get_proxima_semana():
    """Retorna datas da próxima semana"""
    hoje = get_now()
    dia_semana = hoje.weekday()
    
    # Calcular próxima segunda
    if dia_semana == 6:  # Domingo
        dias_ate_proxima_segunda = 1
    else:
        dias_ate_proxima_segunda = 7 - dia_semana
    
    proxima_segunda = hoje + timedelta(days=dias_ate_proxima_segunda)
    
    semana = []
    dias_nome = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    for i in range(5):
        dia = proxima_segunda + timedelta(days=i)
        semana.append({
            "nome": dias_nome[i],
            "data": dia.strftime("%d/%m"),
            "data_completa": dia.strftime("%d/%m/%Y"),
            "objeto": dia
        })
    
    return semana

# =====================================================
# CREDENCIAIS (Variáveis de ambiente ou padrão)
# =====================================================

# Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8217382481:AAHe12yh-31BqjoEB9NwCy5ONuN6kN7QDzs')

# Gmail (para monitorar Notion)
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'millamarttins96@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'ykkb bwgx fugd adjs')

# Trello
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY', 'dec3cd81897d2529e4322f726298e097')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN', 'ATTA2c33cd525ab25d24ac2fbe6cd38508bb75e3fc1161648e9bdb24996024e22289F67DE68F')

# Google Drive
DRIVE_CREDENTIALS = os.getenv('DRIVE_CREDENTIALS', 'karen-bot-486612-4e026f93de8b.json')
DRIVE_EMAIL = 'karen-drive-bot@karen-bot-486612.iam.gserviceaccount.com'

# =====================================================
# QUADROS TRELLO
# =====================================================

TRELLO_BOARDS = {
    # Quadros da equipe
    "Clarysse": {
        "nome": "Designer Clarysse",
        "tipo": "designer",
        "emoji": "👩‍🎨"
    },
    "Larissa": {
        "nome": "Designer Larissa",
        "tipo": "designer",
        "emoji": "👨‍🎨"
    },
    "Bruno": {
        "nome": "EDITOR Bruno",
        "tipo": "editor",
        "emoji": "🎥"
    },
    "Milla": {
        "nome": "Minhas Demandas",
        "tipo": "gerente",
        "emoji": "👤"
    }
}

# Quadros de clientes (19 quadros)
QUADROS_CLIENTES = [
    "Extras - Geral",
    "Plano Crescimento - Carina e Nicole",
    "Plano Crescimento - Daniel Breia",
    "Plano Crescimento - Equestre Matinha",
    "Plano Crescimento - Fabi Beauty",
    "Plano Crescimento - Maria Clara",
    "Plano Crescimento - Pop Decor",
    "Plano Elite - Biomagistral",
    "Plano Elite - Carol Galvão",
    "Plano Elite - Fabricio Melcop",
    "Plano Elite - Gabriela Trevisioli",
    "Plano Elite - Lar & Estilo",
    "Plano Elite - Priscila Saldanha",
    "Plano Impulso - Karen Ferreira",
    "Plano Pontual - Ariella Alves",
    "Plano Pontual - Mariana Melo",
    # Workspace GT
    "Minha Área GT"
]

# =====================================================
# NOTION DATABASES
# =====================================================

NOTION_PAGES = {
    "AC Social Media": {
        "url": "https://www.notion.so/Design-13d4d6b95fc78199a47cc62cb6a98aa9",
        "estrutura": "tabela",
        "campo_cliente": "tabela_header",  # Ex: "ARA-04 - Araceli"
        "campo_titulo": "Nome da postagem",
        "campo_data": "Fazer design",
        "campo_copy": "Planejamento"
    },
    "Asena Marketing": {
        "url": "https://www.notion.so/Design-19939a15596d81d9a1a2f155bca31f11",
        "estrutura": "tabela",
        "campo_cliente": "tabela_header",  # Ex: "DCY-04 - Doutora Carina Yumi"
        "campo_titulo": "Nome da postagem",
        "campo_data": "Fazer design",
        "campo_copy": "Planejamento"
    },
    "Barbalho Marketing": {
        "url": "https://www.notion.so/Design-240fa1fd0b3a814c872cff12f9870186",
        "estrutura": "lista",
        "campo_cliente": "Cliente",
        "campo_titulo": "Nome da postagem",
        "campo_data": "Fazer design",
        "campo_copy": "Copy do conteúdo"  # Dentro do card
    }
}

# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================

PRAZO_ENTREGA = "17:30"
COLUNAS_SEMANA = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
COLUNA_NOVAS = "📥 Novas Demandas"
COLUNA_ALTERACOES = "🔄 Alterações"
COLUNA_PRONTO = "✅ Pronto"
COLUNA_ATENCAO = "⚠️ Atenção"

# Estrutura de pastas Drive
DRIVE_PATH_PATTERN = "{cliente}/Design/{mes}/{titulo}"
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

# =====================================================
# ESTADO DO BOT (temporário - será BD depois)
# =====================================================

BOT_STATE = {
    "ultima_virada": None,
    "demandas_pendentes": [],
    "configuracoes": {
        "virada_automatica": True,
        "dia_virada": 5,  # 5 = Sábado
        "hora_virada": "00:01",
        "mover_pendencias": True
    }
}
