"""
Monitor do Notion - Web Scraping
Monitora 3 páginas do Notion a cada 1 hora
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import aiohttp
from bs4 import BeautifulSoup
import hashlib

logger = logging.getLogger(__name__)


class NotionMonitor:
    """Monitor de demandas do Notion via web scraping"""
    
    def __init__(self):
        self.notion_urls = [
            "https://www.notion.so/Design-13d4d6b95fc78199a47cc62cb6a98aa9",
            "https://www.notion.so/Design-19939a15596d81d9a1a2f155bca31f11",
            "https://www.notion.so/Design-240fa1fd0b3a814c872cff12f9870186"
        ]
        self.last_seen_demands = {}  # Armazenar hash das demandas já vistas
        self.sync_interval = 3600  # 1 hora em segundos
        
    async def start_monitoring(self, bot):
        """Iniciar monitoramento contínuo"""
        logger.info("Monitoramento do Notion iniciado")
        
        while True:
            try:
                await self.check_for_new_demands(bot)
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Erro no monitoramento do Notion: {e}")
                await asyncio.sleep(60)  # Tentar novamente em 1 minuto
                
    async def check_for_new_demands(self, bot):
        """Verificar por novas demandas"""
        logger.info("Verificando Notion por novas demandas...")
        
        for url in self.notion_urls:
            try:
                demands = await self.scrape_notion_page(url)
                
                for demand in demands:
                    demand_hash = self._hash_demand(demand)
                    
                    # Se é uma demanda nova
                    if demand_hash not in self.last_seen_demands:
                        self.last_seen_demands[demand_hash] = True
                        
                        # Verificar se é menção para Milla
                        if self._is_milla_mentioned(demand):
                            logger.info(f"Nova demanda detectada: {demand['title']}")
                            await bot.handle_new_demand(demand)
                            
                        # Verificar se é alteração
                        elif self._is_alteration(demand):
                            logger.info(f"Alteração detectada: {demand['title']}")
                            await bot.handle_alteration(demand)
                            
            except Exception as e:
                logger.error(f"Erro ao fazer scraping da página {url}: {e}")
                
    async def scrape_notion_page(self, url: str) -> List[Dict]:
        """Fazer scraping de uma página do Notion"""
        demands = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        demands = self._parse_notion_html(html, url)
                        
        except Exception as e:
            logger.error(f"Erro ao fazer scraping: {e}")
            
        return demands
        
    def _parse_notion_html(self, html: str, url: str) -> List[Dict]:
        """Parsear HTML do Notion e extrair demandas"""
        demands = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Procurar por elementos de tabela/lista
            # Esta é uma implementação genérica - pode precisar ser ajustada
            # baseada na estrutura real do Notion
            
            # Procurar por divs que contenham informações de demandas
            demand_elements = soup.find_all('div', {'data-block-id': True})
            
            for element in demand_elements:
                demand = self._extract_demand_from_element(element, url)
                if demand:
                    demands.append(demand)
                    
        except Exception as e:
            logger.error(f"Erro ao parsear HTML: {e}")
            
        return demands
        
    def _extract_demand_from_element(self, element, url: str) -> Dict:
        """Extrair informações de demanda de um elemento HTML"""
        try:
            # Extrair título
            title_elem = element.find('span', {'class': 'notion-page-title'})
            title = title_elem.text if title_elem else "N/A"
            
            # Extrair cliente (procurar padrão "XXX-00 - Nome Cliente")
            client_text = element.get_text()
            client = self._extract_client_name(client_text)
            
            # Extrair data de entrega
            date_elem = element.find('span', {'class': 'notion-date'})
            delivery_date = date_elem.text if date_elem else "N/A"
            
            # Extrair copy (procurar em seção de planejamento)
            copy_elem = element.find('div', {'class': 'notion-copy'})
            copy = copy_elem.text if copy_elem else "N/A"
            
            # Gerar ID único
            demand_id = hashlib.md5(f"{title}{client}{delivery_date}".encode()).hexdigest()
            
            return {
                'id': demand_id,
                'title': title,
                'client': client,
                'delivery_date': delivery_date,
                'copy': copy,
                'link': url,
                'source': 'notion',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair demanda: {e}")
            return None
            
    def _extract_client_name(self, text: str) -> str:
        """Extrair nome do cliente do texto"""
        # Procurar padrão "XXX-00 - Nome Cliente"
        import re
        match = re.search(r'([A-Z]{2,})-\d+ - (.+?)(?:\n|$)', text)
        if match:
            return match.group(2).strip()
        return "N/A"
        
    def _is_milla_mentioned(self, demand: Dict) -> bool:
        """Verificar se Milla é mencionada na demanda"""
        # Procurar por menção de Milla no texto
        text = f"{demand.get('title', '')} {demand.get('copy', '')}"
        return 'milla' in text.lower() or '@milla' in text.lower()
        
    def _is_alteration(self, demand: Dict) -> bool:
        """Verificar se é uma alteração"""
        # Procurar por palavras-chave de alteração
        text = f"{demand.get('title', '')} {demand.get('copy', '')}"
        alteration_keywords = ['alteração', 'correção', 'mudança', 'trocar', 'mudar']
        return any(keyword in text.lower() for keyword in alteration_keywords)
        
    def _hash_demand(self, demand: Dict) -> str:
        """Gerar hash de uma demanda para detecção de duplicatas"""
        content = f"{demand.get('title', '')}{demand.get('client', '')}{demand.get('delivery_date', '')}"
        return hashlib.md5(content.encode()).hexdigest()
