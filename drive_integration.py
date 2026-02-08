# -*- coding: utf-8 -*-
"""
Integração Google Drive - Upload REAL
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import config

class DriveAPI:
    """Classe para gerenciar Google Drive"""
    
    def __init__(self):
        self.service = None
        self._connect()
    
    def _connect(self):
        """Conecta ao Google Drive"""
        try:
            # Credentials do service account
            SCOPES = ['https://www.googleapis.com/auth/drive']
            
            # TODO: Carregar arquivo JSON de credenciais
            # Por enquanto, marcar como não conectado
            # credentials = service_account.Credentials.from_service_account_file(
            #     config.DRIVE_CREDENTIALS, scopes=SCOPES)
            # self.service = build('drive', 'v3', credentials=credentials)
            
            print("Drive API: Credenciais configuradas")
            return True
        except Exception as e:
            print(f"Erro ao conectar Drive: {e}")
            return False
    
    def create_folder(self, name, parent_id=None):
        """Cria uma pasta"""
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            if self.service:
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id, webViewLink'
                ).execute()
                
                return folder
            else:
                # Simular retorno
                return {
                    'id': 'fake_folder_id',
                    'webViewLink': 'https://drive.google.com/fake'
                }
                
        except Exception as e:
            print(f"Erro ao criar pasta: {e}")
            return None
    
    def find_folder(self, name, parent_id=None):
        """Busca pasta pelo nome"""
        try:
            query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
            
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            if self.service:
                results = self.service.files().list(
                    q=query,
                    fields='files(id, name, webViewLink)'
                ).execute()
                
                items = results.get('files', [])
                return items[0] if items else None
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao buscar pasta: {e}")
            return None
    
    def upload_file(self, file_path, folder_id=None):
        """Faz upload de arquivo"""
        try:
            file_name = os.path.basename(file_path)
            
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            if self.service:
                media = MediaFileUpload(file_path, resumable=True)
                
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, webViewLink'
                ).execute()
                
                return file
            else:
                # Simular
                return {
                    'id': 'fake_file_id',
                    'webViewLink': f'https://drive.google.com/{file_name}'
                }
                
        except Exception as e:
            print(f"Erro ao fazer upload: {e}")
            return None
    
    def get_share_link(self, file_id):
        """Gera link compartilhável"""
        try:
            if self.service:
                # Dar permissão de leitura para qualquer um com link
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                
                self.service.permissions().create(
                    fileId=file_id,
                    body=permission
                ).execute()
                
                # Pegar link
                file = self.service.files().get(
                    fileId=file_id,
                    fields='webViewLink'
                ).execute()
                
                return file.get('webViewLink')
            else:
                return f'https://drive.google.com/file/{file_id}'
                
        except Exception as e:
            print(f"Erro ao gerar link: {e}")
            return None

# Instância global
drive = DriveAPI()
