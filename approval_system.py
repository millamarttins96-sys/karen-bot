"""
Sistema de Aprovação Simplificado
Etapa 2 - Automações
"""

import logging
import os
from typing import Dict, List
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from trello import TrelloClient
import asyncio

logger = logging.getLogger(__name__)


class ApprovalSystem:
    """Sistema de aprovação de demandas finalizadas"""
    
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        self.client = TrelloClient(api_key=self.api_key, token=self.token)
        self.pending_approvals = {}  # Armazenar aprovações em andamento
        
    async def monitor_ready_cards(self, bot):
        """Monitorar cards que foram movidos para 'Pronto'"""
        logger.info("Monitoramento de cards 'Pronto' iniciado")
        
        while True:
            try:
                await self._check_ready_cards(bot)
                await asyncio.sleep(300)  # Verificar a cada 5 minutos
            except Exception as e:
                logger.error(f"Erro ao monitorar cards prontos: {e}")
                await asyncio.sleep(60)
                
    async def _check_ready_cards(self, bot):
        """Verificar por cards prontos"""
        try:
            # Quadros a monitorar
            boards_to_check = [
                "Designer Clarysse",
                "Designer Larissa",
                "Editor Bruno"
            ]
            
            for board_name in boards_to_check:
                board = self._find_board_by_name(board_name)
                if not board:
                    continue
                    
                # Procurar lista "Pronto"
                lists = board.list_lists()
                ready_list = None
                
                for list_obj in lists:
                    if "pronto" in list_obj.name.lower():
                        ready_list = list_obj
                        break
                        
                if not ready_list:
                    continue
                    
                # Verificar cards na lista "Pronto"
                cards = ready_list.list_cards()
                
                for card in cards:
                    card_id = card.id
                    
                    # Se é um card novo em "Pronto"
                    if card_id not in self.pending_approvals:
                        self.pending_approvals[card_id] = {
                            'card': card,
                            'board_name': board_name,
                            'notified': False
                        }
                        
                        # Notificar usuário
                        await self._notify_ready_card(bot, card, board_name)
                        self.pending_approvals[card_id]['notified'] = True
                        
        except Exception as e:
            logger.error(f"Erro ao verificar cards prontos: {e}")
            
    async def _notify_ready_card(self, bot, card, board_name: str):
        """Notificar quando um card está pronto para aprovação"""
        try:
            # Extrair informações do card
            title = card.name
            description = card.description
            
            # Extrair cliente do nome
            client = self._extract_client_from_card(card)
            
            # Obter arquivos/anexos
            attachments = card.attachments
            
            # Criar mensagem
            message_text = f"""
✅ **{board_name} finalizou!**

📝 **{client}** - {title}

📎 **Arquivos:**
"""
            
            # Adicionar miniaturas dos arquivos
            if attachments:
                for i, attachment in enumerate(attachments[:3], 1):
                    message_text += f"\n{i}. {attachment.get('name', 'Arquivo')}"
            else:
                message_text += "\nSem arquivos anexados"
                
            # Criar botões de aprovação
            keyboard = [
                [
                    InlineKeyboardButton("✅ Aprovar tudo", 
                                       callback_data=f"approve_all_{card.id}"),
                    InlineKeyboardButton("✏️ Pedir alteração", 
                                       callback_data=f"ask_alteration_{card.id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Enviar para o chat do usuário
            await bot.app.bot.send_message(
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            logger.info(f"Notificação de aprovação enviada: {card.id}")
            
        except Exception as e:
            logger.error(f"Erro ao notificar card pronto: {e}")
            
    async def handle_approval(self, query, card_id: str):
        """Lidar com aprovação de card"""
        try:
            # Encontrar o card
            card = self._find_card_by_id(card_id)
            if not card:
                await query.edit_message_text(text="❌ Card não encontrado.")
                return
                
            # Baixar arquivos do Trello
            files = await self._download_card_files(card)
            
            # Identificar cliente
            client = self._extract_client_from_card(card)
            
            # Fazer upload para Google Drive
            drive_link = await self._upload_to_drive(client, card.name, files)
            
            # Enviar confirmação
            confirmation_text = f"""
✅ **Arquivos prontos!**

📝 **Cliente:** {client}
📂 **Pasta:** {card.name}

🔗 **Drive:**
{drive_link}

🔗 **Tarefa Notion:**
[Clique aqui para atualizar]

✅ Confere aí e cola no Notion!
            """
            
            await query.edit_message_text(
                text=confirmation_text,
                parse_mode='Markdown'
            )
            
            # Limpar arquivo de aprovação pendente
            if card_id in self.pending_approvals:
                del self.pending_approvals[card_id]
                
            logger.info(f"Card aprovado: {card_id}")
            
        except Exception as e:
            logger.error(f"Erro ao aprovar card: {e}")
            await query.edit_message_text(text=f"❌ Erro ao aprovar: {str(e)}")
            
    async def handle_alteration_request(self, query, card_id: str):
        """Lidar com solicitação de alteração"""
        try:
            # Perguntar o que precisa mudar
            await query.edit_message_text(
                text="O que precisa mudar?",
                reply_markup=None
            )
            
            # Armazenar estado para próxima mensagem
            self.pending_approvals[card_id]['waiting_for_alteration'] = True
            
            logger.info(f"Aguardando descrição de alteração: {card_id}")
            
        except Exception as e:
            logger.error(f"Erro ao solicitar alteração: {e}")
            
    async def process_alteration_text(self, message, card_id: str, bot):
        """Processar texto de alteração"""
        try:
            alteration_text = message.text
            
            # Encontrar o card
            card = self._find_card_by_id(card_id)
            if not card:
                await message.reply_text("❌ Card não encontrado.")
                return
                
            # Encontrar designer
            board_name = self.pending_approvals[card_id]['board_name']
            designer_name = board_name.replace("Designer ", "").replace("Editor ", "")
            
            # Mover card para "Alterações"
            board = card.board
            lists = board.list_lists()
            alteration_list = None
            
            for list_obj in lists:
                if "alteração" in list_obj.name.lower():
                    alteration_list = list_obj
                    break
                    
            if alteration_list:
                card.change_list(alteration_list.id)
                
            # Adicionar comentário mencionando a designer
            comment_text = f"""
🔄 **ALTERAÇÃO SOLICITADA:**

{alteration_text}

Nova entrega: [Escolher data]
            """
            
            card.comment(comment_text)
            
            # Notificar designer (se houver integração de chat)
            notification = f"""
🔄 **Alteração Solicitada!**

📝 **Demanda:** {card.name}

💬 **O que mudar:**
{alteration_text}

🔗 [Abrir no Trello]({card.url})
            """
            
            await message.reply_text(
                text=notification,
                parse_mode='Markdown'
            )
            
            # Limpar estado
            if card_id in self.pending_approvals:
                del self.pending_approvals[card_id]
                
            logger.info(f"Alteração registrada: {card_id}")
            
        except Exception as e:
            logger.error(f"Erro ao processar alteração: {e}")
            await message.reply_text(f"❌ Erro ao processar alteração: {str(e)}")
            
    async def _download_card_files(self, card) -> List[Dict]:
        """Baixar arquivos do card"""
        files = []
        
        try:
            attachments = card.attachments
            
            for attachment in attachments:
                # Baixar arquivo
                file_url = attachment.get('url')
                file_name = attachment.get('name', 'arquivo')
                
                # Aqui você implementaria o download real
                files.append({
                    'name': file_name,
                    'url': file_url,
                    'path': f'/tmp/{file_name}'
                })
                
        except Exception as e:
            logger.error(f"Erro ao baixar arquivos: {e}")
            
        return files
        
    async def _upload_to_drive(self, client: str, folder_name: str, files: List[Dict]) -> str:
        """Fazer upload para Google Drive"""
        try:
            # Aqui você implementaria o upload real para Google Drive
            # Por enquanto, retornar URL de exemplo
            drive_link = f"https://drive.google.com/drive/folders/exemplo"
            return drive_link
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {e}")
            return "https://drive.google.com"
            
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
            
    def _find_card_by_id(self, card_id: str):
        """Encontrar um card pelo ID"""
        try:
            return self.client.get_card(card_id)
        except Exception as e:
            logger.error(f"Erro ao buscar card: {e}")
            return None
            
    def _extract_client_from_card(self, card) -> str:
        """Extrair nome do cliente do card"""
        # O nome do cliente é geralmente o título do card
        return card.name.split(" - ")[0] if " - " in card.name else card.name
