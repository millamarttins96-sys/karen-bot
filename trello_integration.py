# -*- coding: utf-8 -*-
"""
Integração com Trello - Funções REAIS
"""

import requests
from datetime import datetime
import config

class TrelloAPI:
    """Classe para gerenciar Trello"""
    
    def __init__(self):
        self.api_key = config.TRELLO_API_KEY
        self.token = config.TRELLO_TOKEN
        self.base_url = "https://api.trello.com/1"
        
    def _request(self, method, endpoint, params=None, data=None):
        """Faz requisição à API"""
        url = f"{self.base_url}/{endpoint}"
        auth = {
            'key': self.api_key,
            'token': self.token
        }
        
        if params:
            params.update(auth)
        else:
            params = auth
            
        try:
            if method == 'GET':
                response = requests.get(url, params=params)
            elif method == 'POST':
                response = requests.post(url, params=params, json=data)
            elif method == 'PUT':
                response = requests.put(url, params=params, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, params=params)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro Trello: {e}")
            return None
    
    def get_boards(self):
        """Lista todos os quadros"""
        return self._request('GET', 'members/me/boards')
    
    def get_board_by_name(self, name):
        """Busca quadro pelo nome"""
        boards = self.get_boards()
        if boards:
            for board in boards:
                if name.lower() in board['name'].lower():
                    return board
        return None
    
    def get_lists(self, board_id):
        """Lista todas as colunas de um quadro"""
        return self._request('GET', f'boards/{board_id}/lists')
    
    def get_list_by_name(self, board_id, list_name):
        """Busca coluna pelo nome"""
        lists = self.get_lists(board_id)
        if lists:
            for lst in lists:
                if list_name.lower() in lst['name'].lower():
                    return lst
        return None
    
    def create_card(self, list_id, name, desc=None, due=None, labels=None):
        """Cria um card"""
        data = {
            'idList': list_id,
            'name': name
        }
        
        if desc:
            data['desc'] = desc
        if due:
            data['due'] = due
        if labels:
            data['idLabels'] = labels
            
        return self._request('POST', 'cards', data=data)
    
    def move_card(self, card_id, list_id):
        """Move card para outra coluna"""
        return self._request('PUT', f'cards/{card_id}', data={'idList': list_id})
    
    def add_comment(self, card_id, text):
        """Adiciona comentário no card"""
        return self._request('POST', f'cards/{card_id}/actions/comments', 
                           data={'text': text})
    
    def update_list_name(self, list_id, new_name):
        """Atualiza nome da coluna"""
        return self._request('PUT', f'lists/{list_id}', data={'name': new_name})
    
    def get_cards_in_list(self, list_id):
        """Retorna todos os cards de uma coluna"""
        return self._request('GET', f'lists/{list_id}/cards')
    
    def virar_semana(self, board_name):
        """Atualiza datas das colunas da semana"""
        board = self.get_board_by_name(board_name)
        if not board:
            return False
            
        lists = self.get_lists(board['id'])
        if not lists:
            return False
        
        # Pegar próxima semana
        proxima = config.get_proxima_semana()
        dias_map = {
            'segunda': proxima[0],
            'terça': proxima[1], 
            'terca': proxima[1],
            'quarta': proxima[2],
            'quinta': proxima[3],
            'sexta': proxima[4]
        }
        
        atualizadas = []
        for lst in lists:
            nome_lower = lst['name'].lower()
            
            for dia_nome, dia_data in dias_map.items():
                if dia_nome in nome_lower:
                    # Novo nome com data atualizada
                    novo_nome = f"{dia_data['nome']}-Feira ({dia_data['data']})"
                    
                    # Atualizar
                    result = self.update_list_name(lst['id'], novo_nome)
                    if result:
                        atualizadas.append(novo_nome)
                    break
        
        return atualizadas

# Instância global
trello = TrelloAPI()
