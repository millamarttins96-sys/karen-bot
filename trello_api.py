# -*- coding: utf-8 -*-
"""
TRELLO API - Integração REAL
"""

import requests
import config

class TrelloAPI:
    def __init__(self):
        self.api_key = config.TRELLO_API_KEY
        self.token = config.TRELLO_TOKEN
        self.base_url = "https://api.trello.com/1"
        self.cache_boards = {}
        
    def _request(self, method, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        auth_params = {
            'key': self.api_key,
            'token': self.token
        }
        if params:
            auth_params.update(params)
        
        try:
            if method == 'GET':
                r = requests.get(url, params=auth_params, timeout=10)
            elif method == 'POST':
                r = requests.post(url, params=auth_params, timeout=10)
            elif method == 'PUT':
                r = requests.put(url, params=auth_params, timeout=10)
            
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Erro Trello: {e}")
            return None
    
    def get_boards(self):
        """Lista todos os quadros"""
        return self._request('GET', 'members/me/boards')
    
    def find_board(self, name):
        """Busca quadro pelo nome"""
        if name in self.cache_boards:
            return self.cache_boards[name]
            
        boards = self.get_boards()
        if boards:
            for board in boards:
                if name.lower() in board['name'].lower():
                    self.cache_boards[name] = board
                    return board
        return None
    
    def get_lists(self, board_id):
        """Pega colunas do quadro"""
        return self._request('GET', f'boards/{board_id}/lists')
    
    def find_list(self, board_id, list_name):
        """Busca coluna pelo nome"""
        lists = self.get_lists(board_id)
        if lists:
            for lst in lists:
                if list_name.lower() in lst['name'].lower():
                    return lst
        return None
    
    def create_card(self, list_id, name, desc, due=None):
        """Cria card"""
        params = {
            'idList': list_id,
            'name': name,
            'desc': desc
        }
        if due:
            params['due'] = due
        return self._request('POST', 'cards', params)
    
    def move_card(self, card_id, list_id):
        """Move card"""
        return self._request('PUT', f'cards/{card_id}', {'idList': list_id})
    
    def add_comment(self, card_id, text):
        """Adiciona comentário"""
        return self._request('POST', f'cards/{card_id}/actions/comments', {'text': text})

trello = TrelloAPI()
