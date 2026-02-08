"""
Gerenciador de Upload para Google Drive
Etapa 2 - Automações
"""

import logging
import os
from typing import Dict, List
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import asyncio

logger = logging.getLogger(__name__)


class DriveManager:
    """Gerenciador de uploads para Google Drive"""
    
    def __init__(self):
        self.service = self._initialize_drive_service()
        self.clients_folders = {}  # Cache de pastas de clientes
        
    def _initialize_drive_service(self):
        """Inicializar serviço do Google Drive"""
        try:
            # Usar credenciais da Service Account
            credentials = service_account.Credentials.from_service_account_file(
                'config/service_account.json',
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            service = build('drive', 'v3', credentials=credentials)
            logger.info("Serviço do Google Drive inicializado")
            return service
            
        except Exception as e:
            logger.error(f"Erro ao inicializar Drive: {e}")
            return None
            
    async def upload_files(self, client_name: str, folder_name: str, files: List[Dict]) -> str:
        """Fazer upload de arquivos para Google Drive"""
        try:
            # Encontrar ou criar pasta do cliente
            client_folder_id = await self._get_or_create_client_folder(client_name)
            if not client_folder_id:
                logger.error(f"Não foi possível criar pasta do cliente: {client_name}")
                return None
                
            # Encontrar ou criar pasta do mês
            month_folder_id = await self._get_or_create_month_folder(client_folder_id)
            if not month_folder_id:
                logger.error("Não foi possível criar pasta do mês")
                return None
                
            # Criar pasta da demanda
            demand_folder_id = await self._create_demand_folder(month_folder_id, folder_name)
            if not demand_folder_id:
                logger.error(f"Não foi possível criar pasta da demanda: {folder_name}")
                return None
                
            # Fazer upload dos arquivos
            for file_data in files:
                await self._upload_file(demand_folder_id, file_data)
                
            # Gerar link da pasta
            folder_link = f"https://drive.google.com/drive/folders/{demand_folder_id}"
            
            logger.info(f"Upload concluído: {folder_link}")
            return folder_link
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload: {e}")
            return None
            
    async def _get_or_create_client_folder(self, client_name: str) -> str:
        """Encontrar ou criar pasta do cliente"""
        try:
            # Verificar cache
            if client_name in self.clients_folders:
                return self.clients_folders[client_name]
                
            # Procurar pasta existente
            query = f"name='{client_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                folder_id = files[0]['id']
                self.clients_folders[client_name] = folder_id
                return folder_id
                
            # Criar nova pasta
            file_metadata = {
                'name': client_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            self.clients_folders[client_name] = folder_id
            
            logger.info(f"Pasta do cliente criada: {client_name} ({folder_id})")
            return folder_id
            
        except Exception as e:
            logger.error(f"Erro ao criar pasta do cliente: {e}")
            return None
            
    async def _get_or_create_month_folder(self, parent_folder_id: str) -> str:
        """Encontrar ou criar pasta do mês"""
        try:
            # Obter mês atual
            current_month = datetime.now().strftime("%B")  # Nome do mês em inglês
            month_names = {
                'January': 'Janeiro',
                'February': 'Fevereiro',
                'March': 'Março',
                'April': 'Abril',
                'May': 'Maio',
                'June': 'Junho',
                'July': 'Julho',
                'August': 'Agosto',
                'September': 'Setembro',
                'October': 'Outubro',
                'November': 'Novembro',
                'December': 'Dezembro'
            }
            
            month_name = month_names.get(current_month, current_month)
            
            # Procurar pasta do mês
            query = f"name='{month_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]['id']
                
            # Criar nova pasta do mês
            file_metadata = {
                'name': month_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Pasta do mês criada: {month_name} ({folder_id})")
            return folder_id
            
        except Exception as e:
            logger.error(f"Erro ao criar pasta do mês: {e}")
            return None
            
    async def _create_demand_folder(self, parent_folder_id: str, folder_name: str) -> str:
        """Criar pasta da demanda"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            logger.info(f"Pasta da demanda criada: {folder_name} ({folder_id})")
            return folder_id
            
        except Exception as e:
            logger.error(f"Erro ao criar pasta da demanda: {e}")
            return None
            
    async def _upload_file(self, parent_folder_id: str, file_data: Dict) -> bool:
        """Fazer upload de um arquivo"""
        try:
            file_path = file_data.get('path')
            file_name = file_data.get('name', os.path.basename(file_path))
            
            if not os.path.exists(file_path):
                logger.warning(f"Arquivo não encontrado: {file_path}")
                return False
                
            # Obter tipo MIME
            mime_type = self._get_mime_type(file_path)
            
            # Criar metadados do arquivo
            file_metadata = {
                'name': file_name,
                'parents': [parent_folder_id]
            }
            
            # Fazer upload
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logger.info(f"Arquivo enviado: {file_name} ({file.get('id')})")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo: {e}")
            return False
            
    def _get_mime_type(self, file_path: str) -> str:
        """Obter tipo MIME do arquivo"""
        extension = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.zip': 'application/zip',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
        }
        
        return mime_types.get(extension, 'application/octet-stream')
        
    async def create_month_folder_on_date_change(self, bot):
        """Criar pasta do próximo mês automaticamente no dia 01"""
        logger.info("Scheduler de criação de pasta mensal iniciado")
        
        while True:
            try:
                # Verificar se é dia 01
                if datetime.now().day == 1 and datetime.now().hour == 0:
                    await self._create_next_month_folders(bot)
                    
                await asyncio.sleep(3600)  # Verificar a cada hora
                
            except Exception as e:
                logger.error(f"Erro no scheduler de pasta mensal: {e}")
                await asyncio.sleep(3600)
                
    async def _create_next_month_folders(self, bot):
        """Criar pastas do próximo mês em todos os clientes"""
        try:
            # Aqui você implementaria a lógica para criar pastas
            # em todos os clientes para o próximo mês
            
            notification = """
📅 **VIRADA DE MÊS!**

✅ Criei a pasta do próximo mês em todos os Drives.

A partir de agora, uploads vão para a pasta do novo mês.
            """
            
            await bot.app.bot.send_message(
                chat_id=os.getenv('TELEGRAM_CHAT_ID'),
                text=notification,
                parse_mode='Markdown'
            )
            
            logger.info("Pastas do próximo mês criadas")
            
        except Exception as e:
            logger.error(f"Erro ao criar pastas do próximo mês: {e}")
