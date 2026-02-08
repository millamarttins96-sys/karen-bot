"""
Gerenciador de Semanas
Gerencia virada de semana automática e atualização de datas
"""

import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict
from trello import TrelloClient
import asyncio
import schedule

logger = logging.getLogger(__name__)


class WeekManager:
    """Gerencia semanas e datas das demandas"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.client = TrelloClient(api_key=self.api_key, token=self.token)
        
        # Quadros a atualizar
        self.boards_to_update = [
            "Minhas Demandas",
            "Designer Clarysse",
            "Designer Larissa",
            "Editor Bruno"
        ]
        
    async def start_week_scheduler(self, bot):
        """Iniciar scheduler de virada de semana"""
        logger.info("Scheduler de semana iniciado")
        
        # Agendar virada de semana para Sábado 00:01
        schedule.every().saturday.at("00:01").do(
            lambda: asyncio.create_task(self.turn_week(bot))
        )
        
        # Executar scheduler em background
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)
            
    async def turn_week(self, bot):
        """Executar virada de semana"""
        try:
            logger.info("Iniciando virada de semana automática...")
            
            # Atualizar todos os quadros
            for board_name in self.boards_to_update:
                await self._update_board_week(board_name, bot)
                
            # Enviar relatório
            await self._send_week_report(bot)
            
            logger.info("Virada de semana concluída!")
            
        except Exception as e:
            logger.error(f"Erro na virada de semana: {e}")
            
    async def _update_board_week(self, board_name: str, bot):
        """Atualizar datas de um quadro específico"""
        try:
            board = self._find_board_by_name(board_name)
            if not board:
                logger.warning(f"Quadro não encontrado: {board_name}")
                return
                
            # Calcular próxima semana
            today = datetime.now()
            next_week_start = today + timedelta(days=(5 - today.weekday()))  # Próxima segunda
            
            # Atualizar nomes das listas
            lists = board.list_lists()
            day_names = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira"]
            
            for i, list_obj in enumerate(lists):
                # Procurar listas com padrão de data
                if any(day in list_obj.name for day in day_names):
                    # Calcular nova data
                    new_date = next_week_start + timedelta(days=i)
                    new_name = f"{day_names[i]} ({new_date.strftime('%d/%m')})"
                    
                    # Renomear lista
                    list_obj.name = new_name
                    list_obj.save()
                    
                    logger.info(f"Lista renomeada: {list_obj.name}")
                    
            # Mover cards não concluídos
            await self._move_pending_cards(board, bot)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar quadro {board_name}: {e}")
            
    async def _move_pending_cards(self, board, bot):
        """Mover cards não concluídos para segunda da próxima semana"""
        try:
            # Encontrar lista de "Pronto" ou "Concluído"
            lists = board.list_lists()
            pending_cards = []
            ready_list = None
            
            for list_obj in lists:
                if "pronto" in list_obj.name.lower() or "concluído" in list_obj.name.lower():
                    ready_list = list_obj
                else:
                    # Verificar cards não concluídos
                    cards = list_obj.list_cards()
                    pending_cards.extend(cards)
                    
            if pending_cards:
                # Perguntar ao usuário o que fazer
                await bot.ask_about_pending_cards(board.name, pending_cards)
                
        except Exception as e:
            logger.error(f"Erro ao mover cards: {e}")
            
    async def _send_week_report(self, bot):
        """Enviar relatório de virada de semana"""
        try:
            report = self._generate_week_report()
            await bot.send_report(report)
            
        except Exception as e:
            logger.error(f"Erro ao enviar relatório: {e}")
            
    def _generate_week_report(self) -> str:
        """Gerar relatório de virada de semana"""
        today = datetime.now()
        next_week_start = today + timedelta(days=(5 - today.weekday()))
        
        report = f"""
🔄 **VIRADA DE SEMANA AUTOMÁTICA**
━━━━━━━━━━━━━━━━━━━━━━━━

✅ Atualizei as datas em TODOS os quadros:

📋 Minhas Demandas
📋 Designer Clarysse
📋 Designer Larissa
📋 Editor Bruno

Nova semana: {next_week_start.strftime('%d/%m')} a {(next_week_start + timedelta(days=4)).strftime('%d/%m')}

📊 **RESUMO DA SEMANA ANTERIOR:**
━━━━━━━━━━━━━━━━━━━━━━━━
✅ Concluídas: 0 demandas
⏳ Pendentes: 0 demandas

🤖 Próxima virada: Sábado {(today + timedelta(days=6)).strftime('%d/%m')} 00h
        """
        return report
        
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
            
    async def manual_turn_week(self, bot):
        """Virada de semana manual via comando /virar_semana"""
        await self.turn_week(bot)
