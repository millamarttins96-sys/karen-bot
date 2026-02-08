"""
Dashboard Web
Etapa 3 - Extras
Aplicação Flask para visualizar status em tempo real
"""

import logging
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'sua_chave_secreta_aqui')


class DashboardApp:
    """Aplicação Flask do Dashboard"""
    
    def __init__(self):
        self.app = app
        self.setup_routes()
        
    def setup_routes(self):
        """Configurar rotas da aplicação"""
        
        @self.app.route('/')
        def index():
            """Página principal do dashboard"""
            return render_template('dashboard.html')
            
        @self.app.route('/api/status')
        def get_status():
            """API: Obter status geral"""
            return jsonify({
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'total_demands': 0,
                    'completed': 0,
                    'pending': 0,
                    'delayed': 0
                }
            })
            
        @self.app.route('/api/you')
        def get_you_status():
            """API: Status de Você (Milla)"""
            return jsonify({
                'name': 'Milla',
                'demands': [
                    {
                        'day': 'Segunda-Feira',
                        'total': 2,
                        'completed': 1,
                        'pending': 1
                    },
                    {
                        'day': 'Terça-Feira',
                        'total': 3,
                        'completed': 2,
                        'pending': 1
                    }
                ],
                'performance': 85,
                'this_week': {
                    'completed': 5,
                    'pending': 3
                }
            })
            
        @self.app.route('/api/clarysse')
        def get_clarysse_status():
            """API: Status de Clarysse"""
            return jsonify({
                'name': 'Clarysse',
                'role': 'Designer',
                'demands': [
                    {
                        'day': 'Segunda-Feira',
                        'total': 3,
                        'completed': 2,
                        'pending': 1
                    }
                ],
                'performance': 92,
                'this_week': {
                    'completed': 10,
                    'pending': 2
                }
            })
            
        @self.app.route('/api/larissa')
        def get_larissa_status():
            """API: Status de Larissa"""
            return jsonify({
                'name': 'Larissa',
                'role': 'Designer',
                'demands': [],
                'performance': 88,
                'this_week': {
                    'completed': 8,
                    'pending': 3
                }
            })
            
        @self.app.route('/api/bruno')
        def get_bruno_status():
            """API: Status de Bruno"""
            return jsonify({
                'name': 'Bruno',
                'role': 'Editor',
                'demands': [],
                'performance': 90,
                'this_week': {
                    'completed': 6,
                    'pending': 2
                }
            })
            
        @self.app.route('/api/alerts')
        def get_alerts():
            """API: Obter alertas"""
            return jsonify({
                'alerts': [
                    {
                        'type': 'deadline',
                        'message': 'Demanda atrasada',
                        'priority': 'high',
                        'timestamp': datetime.now().isoformat()
                    }
                ]
            })
            
    def run(self, debug=False, host='0.0.0.0', port=5000):
        """Executar aplicação"""
        logger.info(f"Iniciando Dashboard em {host}:{port}")
        self.app.run(debug=debug, host=host, port=port)


if __name__ == '__main__':
    dashboard = DashboardApp()
    dashboard.run(debug=True)
