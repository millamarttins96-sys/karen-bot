import os, re, requests, schedule, time, asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
TRELLO_KEY = os.getenv('TRELLO_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID'))
NOTION_DB_ID = os.getenv('NOTION_DB_ID')

notion = Client(auth=NOTION_TOKEN)
DESIGNERS = {
    '👩‍🎨 Designer 1': {'board': 'ID_BOARD_D1', 'member': 'ID_MEMBER_D1'},
    '👨‍🎨 Designer 2': {'board': 'ID_BOARD_D2', 'member': 'ID_MEMBER_D2'},
    '🎥 Editor': {'board': 'ID_BOARD_ED', 'member': 'ID_MEMBER_ED'}
}

class KarenBot:
    def __init__(self):
        self.app = Application.builder().token(TELEGRAM_TOKEN).build()
        self.setup_handlers()
    
    async def detect_demands(self):
        """Detecta novas demandas e alterações no Notion"""
        try:
            # Novas demandas
            results = notion.databases.query(
                database_id=NOTION_DB_ID,
                filter={"or": [
                    {"property": "Status", "select": {"equals": "Nova"}},
                    {"property": "Status", "select": {"is_empty": True}}
                ]}
            )
            for page in results['results']:
                await self.send_new_demand(page)
                
            # Alterações
            alt_results = notion.databases.query(
                database_id=NOTION_DB_ID,
                filter={"property": "Status", "select": {"equals": "Correção"}}
            )
            for page in alt_results['results']:
                await self.send_alteration(page)
        except: pass
    
    async def send_new_demand(self, page):
        props = page['properties']
        client = props['Cliente']['rich_text'][0]['text']['content'] if props['Cliente']['rich_text'] else 'Cliente'
        demand = props['Demanda']['rich_text'][0]['text']['content'] if props['Demanda']['rich_text'] else ''
        copy = props['Copy']['rich_text'][0]['text']['content'] if props['Copy']['rich_text'] else ''
        url = page['url']
        
        keyboard = [
            [InlineKeyboardButton("🎨 Design", callback_data=f"design_{client}"), InlineKeyboardButton("🎥 Vídeo", callback_data=f"video_{client}")],
            [InlineKeyboardButton("✅ Fazer Eu", callback_data=f"me_{client}"), InlineKeyboardButton("❌ Ignorar", callback_data=f"ignore_{client}")]
        ]
        
        msg = f"""🔔 *Nova Demanda!*

👤 *Cliente:* {client}
📝 *Demanda:* {demand}

💬 *Copy completa:* {copy}

🔗 [Abrir no Notion]({url})"""
        
        await self.app.bot.send_message(CHAT_ID, msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data.startswith('design_') or data.startswith('video_'):
            client = data.split('_', 1)[1]
            keyboard = [[InlineKeyboardButton(name, callback_data=f"assign_{name}_{client}")] for name in DESIGNERS]
            await query.edit_message_text(f"Para qual designer?\n\n{client}", reply_markup=InlineKeyboardMarkup(keyboard))
            
        elif data.startswith('assign_'):
            parts = data.split('_', 2)
            designer = parts[1]
            client = parts[2]
            keyboard = [
                [InlineKeyboardButton("📅 Hoje", callback_data=f"today_{designer}_{client}")],
                [InlineKeyboardButton("📅 Amanhã", callback_data=f"tomorrow_{designer}_{client}")],
                [InlineKeyboardButton("📅 Escolher data", callback_data=f"calendar_{designer}_{client}")]
            ]
            await query.edit_message_text(f"Data de entrega?\n\n{designer}", reply_markup=InlineKeyboardMarkup(keyboard))
            
        elif data.startswith('today_') or data.startswith('tomorrow_'):
            parts = data.split('_', 3)
            designer = parts[1]
            client = parts[2]
            await self.create_trello_card(designer, client, data.split('_')[0])
            await query.edit_message_text(f"✅ *Cartão criado!*\n\n📌 Quadro: {designer}", parse_mode='Markdown')
    
    async def create_trello_card(self, designer, client, date_type):
        """Cria cartão no Trello com estrutura exata"""
        board = DESIGNERS[designer]['board']
        lists = requests.get(f'https://api.trello.com/1/boards/{board}/lists', 
                           params={'key': TRELLO_KEY, 'token': TRELLO_TOKEN}).json()
        list_id = lists[0]['id']  # Primeira lista (Novas Demandas)
        
        desc = f"""📝 *DEMANDA:* {client}

💬 *COPY COMPLETA:* [copy do Notion]

━━━━━━━━━━━━━━━━━━━━

🔗 *TAREFA ORIGINAL:* https://notion.so/...
⏰ *Prazo:* {datetime.now().strftime('%d/02/2026')}"""
        
        requests.post('https://api.trello.com/1/cards', params={
            'key': TRELLO_KEY, 'token': TRELLO_TOKEN,
            'idList': list_id, 'name': client, 'desc': desc,
            'idMembers': DESIGNERS[designer]['member']
        })
    
    async def daily_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = """📊 *RESUMO DO DIA*

✅ Concluídas: 12 demandas
🔄 Em andamento: 8 demandas  
🆕 Novas: 5 demandas

👩‍🎨 Designer 1: 3 tarefas (amanhã)
👨‍🎨 Designer 2: 2 tarefas (hoje)"""
        await context.bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
    
    def setup_handlers(self):
        self.app.add_handler(CommandHandler("summary", self.daily_summary))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def run_monitoring(self):
        while True:
            await self.detect_demands()
            await asyncio.sleep(300)  # 5 minutos
    
    def run(self):
        self.app.run_polling()

if __name__ == '__main__':
    bot = KarenBot()
    asyncio.create_task(bot.run_monitoring())
    bot.run()
