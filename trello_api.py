# -*- coding: utf-8 -*-
"""
API TRELLO - Integração REAL
"""

import requests
import os

class TrelloAPI:
    def __init__(self):
        self.api_key = os.getenv('TRELLO_API_KEY', '619499218f9824db789a7733a2f8874a')
        self.token = os.getenv('TRELLO_TOKEN', 'ATTA8e784bcc242cd373059b1db8601a076a0eb84d623c12b308c1d156a94ce97f2872889884')
        self.base_url = "https://api.trello.com/1"
        
    def _request(self, method, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        auth = {
            'key': self.api_key,
            'token': self.token
        }
        if params:
            auth.update(params)
        
        try:
            if method == 'GET':
                r = requests.get(url, params=auth, timeout=10)
            elif method == 'POST':
                r = requests.post(url, params=auth, timeout=10)
            
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"❌ Erro Trello: {e}")
            return None
    
    def get_boards(self):
        """Lista todos os quadros"""
        return self._request('GET', 'members/me/boards')
    
    def find_board(self, name):
        """Busca quadro pelo nome"""
        boards = self.get_boards()
        if boards:
            for board in boards:
                if name.lower() in board['name'].lower():
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

trello = TrelloAPI()
