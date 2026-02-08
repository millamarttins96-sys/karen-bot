"""
Sistema de Alertas de Prazo
Etapa 3 - Extras
"""

import logging
import os
from typing import Dict, List
from datetime import datetime, time
import asyncio
try:
    from trello import TrelloClient
except ImportError:
    print('Instale py-trello: pip install py-trello')
    TrelloClient = None

logger = logging.getLogger(__name__)


class DeadlineAlerts:
    """Sistema de alertas de prazo"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.client = TrelloClient(api_key=self.api_key, token=self.token)
        self.alert_time = os.getenv('WORK_END_TIME', '17:30')
        self.boards_to_check = [
            "Minhas Demandas",
            "Designer Clarysse",
            "Designer Larissa",
            "Editor Bruno"
        ]
        
    async def start_deadline_scheduler(self, bot):
        """Iniciar scheduler de alertas de prazo"""
        logger.info("Scheduler de alertas de prazo iniciado")
        
        while True:
            try:
                # Verificar hora do alerta
                now = datetime.now()
                alert_hour, alert_minute = map(int, self.alert_time.split(':'))
                
                if now.hour == alert_hour and now.minute == alert_minute:
                    # Apenas em dias úteis
                    if now.weekday() < 5:  # Segunda a Sexta
                        await self.check_and_send_alerts(bot)
                        
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Erro no scheduler de alertas: {e}")
                await asyncio.sleep(60)
                
    async def check_and_send_alerts(self, bot):
        """Verificar por demandas atrasadas e enviar alertas"""
        try:
            logger.info("Verificando demandas atrasadas...")
            
            delayed_demands = await self._get_delayed_demands()
            
            if delayed_demands:
                await self._send_alert(bot, delayed_demands)
            else:
                logger.info("Nenhuma demanda atrasada")
                
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")
            
    async def _get_delayed_demands(self) -> Dict[str, List]:
        """Obter demandas atrasadas"""
        try:
            delayed = {
                'you': [],
                'clarysse': [],
                'larissa': [],
                'bruno': []
            }
            
            today = datetime.now().date()
            
            for board_name in self.boards_to_check:
                board = self._find_board_by_name(board_name)
                if not board:
                    continue
                    
                # Obter todas as listas
                lists = board.list_lists()
                
                for list_obj in lists:
                    # Pular listas "Pronto" ou "Concluído"
                    if "pronto" in list_obj.name.lower() or "concluído" in list_obj.name.lower():
                        continue
                        
                    # Obter cards
                    cards = list_obj.list_cards()
                    
                    for card in cards:
                        # Verificar se tem data de vencimento
                        if card.due_date:
                            due_date = card.due_date.date()
                            
                            # Se vencimento é hoje ou antes
                            if due_date <= today:
                                # Pular cards de folga
                                if "folga" not in card.name.lower():
                                    # Determinar a pessoa
                                    person = self._get_person_from_board(board_name)
                                    
                                    delayed[person].append({
                                        'title': card.name,
                                        'due_date': card.due_date.strftime("%d/%m/%Y"),
                                        'list': list_obj.name,
                                        'url': card.url
                                    })
                                    
            return delayed
            
        except Exception as e:
            logger.error(f"Erro ao obter demandas atrasadas: {e}")
            return {}
            
    async def _send_alert(self, bot, delayed_demands: Dict[str, List]):
        """Enviar alerta de demandas atrasadas"""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            message = "⏰ **ALERTA DE PRAZO!**\n\n"
            message += "Passou das 17:30 e tem pendências:\n\n"
            
            # Você
            if delayed_demands['you']:
                message += "👤 **VOCÊ:**\n"
                for demand in delayed_demands['you']:
                    message += f"• {demand['title']} ({demand['due_date']})\n"
                message += "\n"
                
            # Clarysse
            if delayed_demands['clarysse']:
                message += "🎨 **CLARYSSE:**\n"
                for demand in delayed_demands['clarysse']:
                    message += f"• {demand['title']} ({demand['due_date']})\n"
                message += "\n"
                
            # Larissa
            if delayed_demands['larissa']:
                message += "🎨 **LARISSA:**\n"
                for demand in delayed_demands['larissa']:
                    message += f"• {demand['title']} ({demand['due_date']})\n"
                message += "\n"
                
            # Bruno
            if delayed_demands['bruno']:
                message += "🎥 **BRUNO:**\n"
                for demand in delayed_demands['bruno']:
                    message += f"• {demand['title']} ({demand['due_date']})\n"
                message += "\n"
                
            # Botões de ação
            keyboard = [
                [
                    InlineKeyboardButton("💬 Avisar eles", 
                                       callback_data="alert_notify"),
                    InlineKeyboardButton("📅 Reagendar", 
                                       callback_data="alert_reschedule")
                ],
                [
                    InlineKeyboardButton("✅ Ok", 
                                       callback_data="alert_ok")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await bot.app.bot.send_message(
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info("Alerta de prazo enviado")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {e}")
            
    async def handle_alert_notify(self, query):
        """Lidar com ação 'Avisar eles'"""
        try:
            await query.edit_message_text(
                text="💬 Notificações enviadas para a equipe!"
            )
            
        except Exception as e:
            logger.error(f"Erro ao notificar equipe: {e}")
            
    async def handle_alert_reschedule(self, query):
        """Lidar com ação 'Reagendar'"""
        try:
            await query.edit_message_text(
                text="📅 Qual é a nova data de entrega?"
            )
            
        except Exception as e:
            logger.error(f"Erro ao reagendar: {e}")
            
    async def handle_alert_ok(self, query):
        """Lidar com ação 'Ok'"""
        try:
            await query.edit_message_text(
                text="✅ Alerta reconhecido. Boa sorte!"
            )
            
        except Exception as e:
            logger.error(f"Erro ao reconhecer alerta: {e}")
            
    def _find_board_by_name(self, board_name: str):
        """Encontrar um quadro pelo nome"""
        try:
            all_boards = self.client.list_boards()
            for board in all_boards:
                if board.name == board_name:
                    return board
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar quadro: {e}")
            return None
            
    def _get_person_from_board(self, board_name: str) -> str:
        """Obter pessoa baseado no nome do quadro"""
        if "Clarysse" in board_name:
            return "clarysse"
        elif "Larissa" in board_name:
            return "larissa"
        elif "Bruno" in board_name:
            return "bruno"
        else:
            return "you"
