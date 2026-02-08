"""
Monitor do Trello
Monitora 19 quadros de clientes + Trello GT
"""

import asyncio
import logging
from typing import List, Dict
import os
from trello import TrelloClient
import hashlib

logger = logging.getLogger(__name__)


class TrelloMonitor:
    """Monitor de demandas do Trello via API"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.client = TrelloClient(api_key=self.api_key, token=self.token)
        
        # Quadros a monitorar
        self.client_boards = [
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
            "Plano Pontual - Mariana Melo",
            "Minha Área GT"  # Quadro especial do cliente
        ]
        
        self.last_seen_cards = {}  # Armazenar hash dos cards já vistos
        self.sync_interval = 300  # 5 minutos em segundos
        
    async def start_monitoring(self, bot):
        """Iniciar monitoramento contínuo"""
        logger.info("Monitoramento do Trello iniciado")
        
        while True:
            try:
                await self.check_for_new_cards(bot)
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Erro no monitoramento do Trello: {e}")
                await asyncio.sleep(60)
                
    async def check_for_new_cards(self, bot):
        """Verificar por novos cards"""
        logger.info("Verificando Trello por novos cards...")
        
        try:
            # Buscar todos os quadros
            all_boards = self.client.list_boards()
            
            for board in all_boards:
                # Verificar se é um quadro que devemos monitorar
                if self._should_monitor_board(board.name):
                    await self._check_board_for_cards(board, bot)
                    
        except Exception as e:
            logger.error(f"Erro ao verificar Trello: {e}")
            
    async def _check_board_for_cards(self, board, bot):
        """Verificar um quadro específico por novos cards"""
        try:
            # Obter todas as listas do quadro
            lists = board.list_lists()
            
            for list_obj in lists:
                # Obter todos os cards da lista
                cards = list_obj.list_cards()
                
                for card in cards:
                    card_hash = self._hash_card(card)
                    
                    # Se é um card novo
                    if card_hash not in self.last_seen_cards:
                        self.last_seen_cards[card_hash] = True
                        
                        # Verificar se tem etiqueta "AGUARDANDO DESIGN"
                        if self._has_label(card, "AGUARDANDO DESIGN"):
                            logger.info(f"Nova demanda no Trello: {card.name}")
                            demand = self._convert_card_to_demand(card, board.name)
                            await bot.handle_new_demand(demand)
                            
                        # Verificar se tem etiqueta "ALTERAÇÃO"
                        elif self._has_label(card, "ALTERAÇÃO"):
                            logger.info(f"Alteração no Trello: {card.name}")
                            demand = self._convert_card_to_demand(card, board.name)
                            await bot.handle_alteration(demand)
                            
        except Exception as e:
            logger.error(f"Erro ao verificar board: {e}")
            
    def _should_monitor_board(self, board_name: str) -> bool:
        """Verificar se devemos monitorar este quadro"""
        return board_name in self.client_boards
        
    def _has_label(self, card, label_name: str) -> bool:
        """Verificar se card tem uma etiqueta específica"""
        try:
            labels = card.labels
            return any(label.name == label_name for label in labels)
        except:
            return False
            
    def _convert_card_to_demand(self, card, board_name: str) -> Dict:
        """Converter um card do Trello em formato de demanda"""
        try:
            # Extrair informações do card
            title = card.name
            
            # Extrair cliente do nome do quadro
            client = self._extract_client_from_board(board_name)
            
            # Extrair copy dos comentários (procurar por "Card" ou "Roteiro")
            copy = self._extract_copy_from_comments(card)
            
            # Extrair data de entrega (se houver)
            delivery_date = "N/A"
            if card.due_date:
                delivery_date = card.due_date.strftime("%d/%m/%Y")
                
            return {
                'id': card.id,
                'title': title,
                'client': client,
                'delivery_date': delivery_date,
                'copy': copy,
                'link': card.url,
                'source': 'trello',
                'board_name': board_name,
                'timestamp': str(card.date_last_activity)
            }
            
        except Exception as e:
            logger.error(f"Erro ao converter card: {e}")
            return None
            
    def _extract_client_from_board(self, board_name: str) -> str:
        """Extrair nome do cliente do nome do quadro"""
        # Remover prefixos como "Plano Crescimento -", "Plano Elite -", etc.
        prefixes = [
            "Plano Crescimento - ",
            "Plano Elite - ",
            "Plano Impulso - ",
            "Plano Pontual - ",
            "Extras - "
        ]
        
        client = board_name
        for prefix in prefixes:
            if board_name.startswith(prefix):
                client = board_name[len(prefix):]
                break
                
        return client
        
    def _extract_copy_from_comments(self, card) -> str:
        """Extrair copy dos comentários do card"""
        try:
            copy = ""
            comments = card.get_comments()
            
            for comment in comments:
                text = comment.get('data', {}).get('text', '')
                # Procurar por comentários que contenham "Card" ou "Roteiro"
                if 'card' in text.lower() or 'roteiro' in text.lower():
                    copy = text
                    break
                    
            return copy if copy else "N/A"
            
        except Exception as e:
            logger.error(f"Erro ao extrair copy: {e}")
            return "N/A"
            
    def _hash_card(self, card) -> str:
        """Gerar hash de um card para detecção de duplicatas"""
        content = f"{card.id}{card.name}{card.date_last_activity}"
        return hashlib.md5(content.encode()).hexdigest()
