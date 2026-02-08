# -*- coding: utf-8 -*-
"""
KAREN BOT - Configurações
"""

from datetime import datetime, timezone, timedelta

# =====================================================
# FUSO HORÁRIO BRASIL
# =====================================================

BRASILIA_TZ = timezone(timedelta(hours=-3))

def get_now():
    """Retorna data/hora atual em Brasília"""
    return datetime.now(BRASILIA_TZ)

def get_data_atual():
    """Retorna data atual formatada"""
    return get_now().strftime("%d/%m/%Y")

def get_hora_atual():
    """Retorna hora atual formatada"""
    return get_now().strftime("%H:%M")

def get_dia_semana():
    """Retorna dia da semana em português"""
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    return dias[get_now().weekday()]

def get_semana_atual():
    """Retorna datas da semana atual (segunda a sexta)"""
    hoje = get_now()
    dia_semana = hoje.weekday()  # 0=segunda, 6=domingo
    
    # Calcular segunda-feira desta semana
    dias_ate_segunda = dia_semana
    segunda = hoje - timedelta(days=dias_ate_segunda)
    
    # Se hoje é sábado ou domingo, pegar próxima semana
    if dia_semana >= 5:  # 5=sábado, 6=domingo
        segunda = segunda + timedelta(days=7)
    
    semana = []
    for i in range(5):  # Segunda a sexta
        dia = segunda + timedelta(days=i)
        semana.append({
            "nome": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"][i],
            "data": dia.strftime("%d/%m"),
            "data_completa": dia.strftime("%d/%m/%Y")
        })
    
    return semana

def get_proxima_semana():
    """Retorna datas da próxima semana (segunda a sexta)"""
    hoje = get_now()
    dia_semana = hoje.weekday()
    
    # Calcular próxima segunda-feira
    dias_ate_proxima_segunda = 7 - dia_semana
    if dia_semana == 0:  # Se hoje é segunda
        dias_ate_proxima_segunda = 7
    
    proxima_segunda = hoje + timedelta(days=dias_ate_proxima_segunda)
    
    semana = []
    for i in range(5):
        dia = proxima_segunda + timedelta(days=i)
        semana.append({
            "nome": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"][i],
            "data": dia.strftime("%d/%m"),
            "data_completa": dia.strftime("%d/%m/%Y")
        })
    
    return semana

# =====================================================
# CREDENCIAIS
# =====================================================

TELEGRAM_BOT_TOKEN = "8217382481:AAHe12yh-31BqjoEB9NwCy5ONuN6kN7QDzs"

# Gmail
GMAIL_EMAIL = "millamarttins96@gmail.com"
GMAIL_APP_PASSWORD = "ykkb bwgx fugd adjs"

# Trello
TRELLO_API_KEY = "dec3cd81897d2529e4322f726298e097"
TRELLO_TOKEN = "ATTA50ef1c1b7c80a634b92775d4b2b2c8b93de5cf7c0f3d0f5f0a9a77c8e8be6d8cD48B0E37"

# Google Drive
DRIVE_CREDENTIALS_FILE = "karen-bot-486612-4e026f93de8b.json"

# =====================================================
# NOTION DATABASES
# =====================================================

NOTION_PAGES = {
    "AC Social Media": {
        "database_id": "ac-social-media-db",
        "email_domain": "@acsocialmedia"
    },
    "Asena Marketing": {
        "database_id": "asena-marketing-db", 
        "email_domain": "@asenamarketing"
    },
    "Barbalho Marketing": {
        "database_id": "barbalho-marketing-db",
        "email_domain": "@barbalhomarketing"
    }
}

# =====================================================
# TRELLO BOARDS
# =====================================================

TRELLO_BOARDS = {
    # Quadros de clientes
    "Araceli": "board_araceli_id",
    "Doutora Carina Yumi": "board_carina_id",
    "Priscila Saldanha": "board_priscila_id",
    "Carol Galvão": "board_carol_id",
    "Gabriela Trevisioli": "board_gabriela_id",
    "Fabi Beauty": "board_fabi_id",
    "Pop Decor": "board_popdecor_id",
    "Biomagistral": "board_biomagistral_id",
    "Equestre Matinha": "board_equestre_id",
    "Daniel Breia": "board_daniel_id",
    
    # Quadros da equipe
    "Clarysse": "board_clarysse_id",
    "Larissa": "board_larissa_id",
    "Bruno": "board_bruno_id",
    
    # Quadro Milla
    "Milla": "board_milla_id",
    
    # Workspace GT
    "GT Workspace": "board_gt_id"
}

# =====================================================
# EQUIPE
# =====================================================

EQUIPE = {
    "clarysse": {
        "nome": "Clarysse",
        "tipo": "designer",
        "emoji": "👩‍🎨"
    },
    "larissa": {
        "nome": "Larissa",
        "tipo": "designer", 
        "emoji": "👨‍🎨"
    },
    "bruno": {
        "nome": "Bruno",
        "tipo": "editor",
        "emoji": "🎥"
    }
}

# =====================================================
# CONFIGURAÇÕES GERAIS
# =====================================================

PRAZO_ENTREGA = "17:30"
COLUNAS_SEMANA = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
COLUNA_PRONTO = "Pronto"
COLUNA_ATENCAO = "Atenção"  # Quadro Milla

# =====================================================
# ESTADO DO BOT (será substituído por banco de dados)
# =====================================================

BOT_STATE = {
    "demandas": [],
    "equipe": {
        "clarysse": {
            "em_andamento": [],
            "concluidas": [],
            "prontas": []
        },
        "larissa": {
            "em_andamento": [],
            "concluidas": [],
            "prontas": []
        },
        "bruno": {
            "em_andamento": [],
            "concluidas": [],
            "prontas": []
        }
    },
    "ultima_virada_semana": None
}
