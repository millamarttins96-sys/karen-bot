"""
Handler de Distribuição
Gerencia a distribuição de demandas para a equipe
"""

import logging
import os
from typing import Dict
try:
    from trello import TrelloClient
except ImportError:
    print('Instale py-trello: pip install py-trello')
    TrelloClient = None
from datetime import datetime

logger = logging.getLogger(__name__)


class DistributionHandler:
    """Gerencia distribuição de demandas"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.client = TrelloClient(api_key=self.api_key, token=self.token)
        
        # Nomes dos quadros
        self.designer_1_board_name = "Designer Clarysse"
        self.designer_2_board_name = "Designer Larissa"
        self.editor_board_name = "Editor Bruno"
        self.my_board_name = "Minhas Demandas"
        
    async def distribute_to_designer(self, demand: Dict, designer: str, delivery_date: str) -> bool:
        """Distribuir demanda para um designer"""
        try:
            # Selecionar quadro baseado no designer
            if designer == "clarysse":
                board_name = self.designer_1_board_name
                member_name = "Clarysse"
            elif designer == "larissa":
                board_name = self.designer_2_board_name
                member_name = "Larissa"
            elif designer == "bruno":
                board_name = self.editor_board_name
                member_name = "Bruno"
            else:
                logger.error(f"Designer desconhecido: {designer}")
                return False
                
            # Buscar o quadro
            board = self._find_board_by_name(board_name)
            if not board:
                logger.error(f"Quadro não encontrado: {board_name}")
                return False
                
            # Criar card na coluna correta
            list_obj = self._find_or_create_list(board, delivery_date)
            if not list_obj:
                logger.error(f"Não foi possível criar/encontrar lista para {delivery_date}")
                return False
                
            # Criar o card
            card_data = {
                'name': demand.get('client', 'N/A'),
                'desc': self._format_card_description(demand),
                'due': delivery_date,
                'idList': list_obj.id
            }
            
            card = board.add_card(**card_data)
            
            # Adicionar labels
            self._add_labels_to_card(card, demand)
            
            # Adicionar membro
            self._add_member_to_card(card, member_name)
            
            logger.info(f"Card criado com sucesso: {card.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao distribuir demanda: {e}")
            return False
            
    async def distribute_to_me(self, demand: Dict, day_of_week: int) -> bool:
        """Distribuir demanda para você (Milla)"""
        try:
            # Buscar o quadro "Minhas Demandas"
            board = self._find_board_by_name(self.my_board_name)
            if not board:
                logger.error(f"Quadro não encontrado: {self.my_board_name}")
                return False
                
            # Calcular data baseada no dia da semana
            from datetime import datetime, timedelta
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
            delivery_date = week_start + timedelta(days=day_of_week)
            
            # Encontrar lista do dia
            day_names = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            list_name = f"{day_names[day_of_week]} ({delivery_date.strftime('%d/%m')})"
            
            list_obj = self._find_or_create_list(board, list_name)
            if not list_obj:
                logger.error(f"Não foi possível encontrar lista: {list_name}")
                return False
                
            # Criar o card
            card_data = {
                'name': demand.get('client', 'N/A'),
                'desc': self._format_card_description(demand),
                'due': delivery_date.strftime("%Y-%m-%d"),
                'idList': list_obj.id
            }
            
            card = board.add_card(**card_data)
            
            # Adicionar labels
            self._add_labels_to_card(card, demand)
            
            logger.info(f"Card criado em 'Minhas Demandas': {card.id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao distribuir para você: {e}")
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
            
    def _find_or_create_list(self, board, list_name: str):
        """Encontrar ou criar uma lista no quadro"""
        try:
            # Procurar lista existente
            lists = board.list_lists()
            for list_obj in lists:
                if list_obj.name == list_name:
                    return list_obj
                    
            # Se não encontrar, criar nova
            new_list = board.add_list(list_name)
            return new_list
            
        except Exception as e:
            logger.error(f"Erro ao encontrar/criar lista: {e}")
            return None
            
    def _format_card_description(self, demand: Dict) -> str:
        """Formatar descrição do card"""
        description = f"""
📝 **DEMANDA:**
{demand.get('title', 'N/A')}

💬 **COPY COMPLETA:**
{demand.get('copy', 'N/A')}

🔗 **TAREFA ORIGINAL:**
{demand.get('link', 'N/A')}
        """
        return description
        
    def _add_labels_to_card(self, card, demand: Dict):
        """Adicionar labels ao card"""
        try:
            labels = [
                "🆕 Nova Demanda",
                demand.get('client', 'Cliente')
            ]
            
            for label_name in labels:
                # Procurar label existente ou criar nova
                board_labels = card.board.get_labels()
                label_found = False
                
                for label in board_labels:
                    if label.name == label_name:
                        card.add_label(label)
                        label_found = True
                        break
                        
                if not label_found:
                    # Criar nova label
                    new_label = card.board.add_label(label_name, "blue")
                    card.add_label(new_label)
                    
        except Exception as e:
            logger.error(f"Erro ao adicionar labels: {e}")
            
    def _add_member_to_card(self, card, member_name: str):
        """Adicionar membro ao card"""
        try:
            # Procurar membro no quadro
            board_members = card.board.get_members()
            
            for member in board_members:
                if member_name.lower() in member.full_name.lower():
                    card.add_member(member)
                    return True
                    
            logger.warning(f"Membro não encontrado: {member_name}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao adicionar membro: {e}")
            return False
