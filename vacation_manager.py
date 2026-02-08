"""
Gerenciador de Folgas Inteligente
Etapa 2 - Automações
"""

import logging
import os
from typing import Dict
from datetime import datetime, timedelta
from trello import TrelloClient

logger = logging.getLogger(__name__)


class VacationManager:
    """Gerenciador de folgas e dias sem demandas"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.client = TrelloClient(api_key=self.api_key, token=self.token)
        self.vacation_days = {}  # Armazenar dias de folga
        
    async def check_empty_days(self, board_name: str, designer_name: str, day_of_week: int, bot) -> bool:
        """Verificar se um dia está vazio e perguntar se é folga"""
        try:
            # Encontrar o quadro
            board = self._find_board_by_name(board_name)
            if not board:
                return False
                
            # Calcular data do dia
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            target_date = week_start + timedelta(days=day_of_week)
            
            # Encontrar lista do dia
            day_names = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            list_name = f"{day_names[day_of_week]} ({target_date.strftime('%d/%m')})"
            
            # Procurar lista
            lists = board.list_lists()
            target_list = None
            
            for list_obj in lists:
                if list_name in list_obj.name:
                    target_list = list_obj
                    break
                    
            if not target_list:
                return False
                
            # Verificar se lista está vazia
            cards = target_list.list_cards()
            
            # Filtrar cards de folga
            non_vacation_cards = [
                card for card in cards 
                if "folga" not in card.name.lower()
            ]
            
            if len(non_vacation_cards) == 0:
                # Lista vazia, perguntar sobre folga
                await self._ask_about_vacation(bot, designer_name, target_date, board)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar dias vazios: {e}")
            return False
            
    async def _ask_about_vacation(self, bot, designer_name: str, date: datetime, board):
        """Perguntar se é dia de folga"""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            date_str = date.strftime("%d/%m")
            
            message_text = f"""
👀 **Opa! Notei que...**

{designer_name} não tem demandas em {date_str}.

Ela vai ter folga nesse dia?
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Sim, folga", 
                                       callback_data=f"vacation_yes_{designer_name}_{date_str}"),
                    InlineKeyboardButton("❌ Não, pode distribuir", 
                                       callback_data=f"vacation_no_{designer_name}_{date_str}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await bot.app.bot.send_message(
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"Pergunta sobre folga enviada: {designer_name} em {date_str}")
            
        except Exception as e:
            logger.error(f"Erro ao perguntar sobre folga: {e}")
            
    async def handle_vacation_response(self, query, response: str, designer_name: str, date_str: str, board_name: str):
        """Lidar com resposta sobre folga"""
        try:
            if response == "yes":
                # Criar card de folga
                await self._create_vacation_card(board_name, designer_name, date_str)
                await query.edit_message_text(text="✅ Folga registrada!")
                
            else:
                # Permitir distribuição
                await query.edit_message_text(text="❌ Ok, pode distribuir demandas para esse dia.")
                
        except Exception as e:
            logger.error(f"Erro ao processar resposta de folga: {e}")
            await query.edit_message_text(text=f"❌ Erro: {str(e)}")
            
    async def _create_vacation_card(self, board_name: str, designer_name: str, date_str: str):
        """Criar card de folga"""
        try:
            # Encontrar o quadro
            board = self._find_board_by_name(board_name)
            if not board:
                logger.error(f"Quadro não encontrado: {board_name}")
                return
                
            # Encontrar lista do dia
            day_names = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            list_name = f"{day_names[int(date_str.split('/')[0]) % 5]} ({date_str})"
            
            # Procurar lista
            lists = board.list_lists()
            target_list = None
            
            for list_obj in lists:
                if date_str in list_obj.name:
                    target_list = list_obj
                    break
                    
            if not target_list:
                logger.warning(f"Lista não encontrada: {list_name}")
                return
                
            # Criar card de folga
            card_data = {
                'name': '🏖 FOLGA',
                'desc': f'{designer_name} está de folga hoje!\n\nNão distribuir demandas.',
                'idList': target_list.id
            }
            
            card = board.add_card(**card_data)
            
            # Adicionar label de folga
            self._add_vacation_label(card)
            
            logger.info(f"Card de folga criado: {card.id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar card de folga: {e}")
            
    def _add_vacation_label(self, card):
        """Adicionar label de folga ao card"""
        try:
            board_labels = card.board.get_labels()
            
            for label in board_labels:
                if "folga" in label.name.lower():
                    card.add_label(label)
                    return True
                    
            # Criar nova label se não existir
            new_label = card.board.add_label("🏖 Folga", "green")
            card.add_label(new_label)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar label de folga: {e}")
            return False
            
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
