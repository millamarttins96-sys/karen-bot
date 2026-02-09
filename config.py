# -*- coding: utf-8 -*-
"""
CONFIGURAÇÕES KAREN BOT
Todas as credenciais e configurações
"""

import os
from datetime import datetime, timezone, timedelta

# =====================================================
# FUSO HORÁRIO BRASIL
# =====================================================
BRASILIA_TZ = timezone(timedelta(hours=-3))

def get_now():
    return datetime.now(BRASILIA_TZ)

def get_semana_atual():
    hoje = get_now()
    dia_semana = hoje.weekday()
    dias_ate_segunda = dia_semana
    segunda = hoje - timedelta(days=dias_ate_segunda)
    
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
            "callback": f"dia_{i}"
        })
    return semana

# =====================================================
# CREDENCIAIS
# =====================================================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8217382481:AAHe12yh-31BqjoEB9NwCy5ONuN6kN7QDzs')
GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'millamarttins96@gmail.com')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'ykkb bwgx fugd adjs')
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY', 'dec3cd81897d2529e4322f726298e097')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN', 'ATTA50ef1c1b7c80a634b92775d4b2b2c8b93de5cf7c0f3d0f5f0a9a77c8e8be6d8cD48B0E37')

# =====================================================
# EQUIPE
# =====================================================
EQUIPE = {
    "clarysse": {
        "nome": "Designer Clarysse",
        "emoji": "👩‍🎨",
        "quadro": "Designer Clarysse"
    },
    "larissa": {
        "nome": "Designer Larissa", 
        "emoji": "👨‍🎨",
        "quadro": "Designer Larissa"
    },
    "bruno": {
        "nome": "EDITOR Bruno",
        "emoji": "🎥",
        "quadro": "EDITOR Bruno"
    },
    "milla": {
        "nome": "Suas Demandas",
        "emoji": "👤",
        "quadro": "Minhas Demandas"
    }
}

# =====================================================
# NOTION
# =====================================================
NOTION_PAGES = {
    "AC Social Media": {
        "url": "https://www.notion.so/Design-13d4d6b95fc78199a47cc62cb6a98aa9",
        "tipo": "tabela",
        "campo_cliente": "header",
        "campo_titulo": "Nome da postagem",
        "campo_data": "Fazer design",
        "campo_copy": "Planejamento"
    },
    "Asena Marketing": {
        "url": "https://www.notion.so/Design-19939a15596d81d9a1a2f155bca31f11",
        "tipo": "tabela",
        "campo_cliente": "header",
        "campo_titulo": "Nome da postagem",
        "campo_data": "Fazer design",
        "campo_copy": "Planejamento"
    },
    "Barbalho Marketing": {
        "url": "https://www.notion.so/Design-240fa1fd0b3a814c872cff12f9870186",
        "tipo": "lista",
        "campo_cliente": "Cliente",
        "campo_titulo": "Nome da postagem",
        "campo_data": "Fazer design",
        "campo_copy": "Copy do conteúdo"
    }
}

# =====================================================
# QUADROS TRELLO CLIENTES
# =====================================================
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
    "Plano Elite - Fabrício Melcop",
    "Plano Elite - Gabriela Trevisioli",
    "Plano Elite - Lar & Estilo",
    "Plano Elite - Priscila Saldanha",
    "Plano Impulso - Karen Ferreira",
    "Plano Pontual - Ariella Alves",
    "Plano Pontual - Mariana Melo"
]

# Cliente externo (Trello próprio)
QUADRO_GT = "Minha Área GT"

# =====================================================
# CONFIGURAÇÕES
# =====================================================
PRAZO_ENTREGA = "17:30"
INTERVALO_CHECK_GMAIL = 300  # 5 minutos
INTERVALO_CHECK_TRELLO = 180  # 3 minutos
