# 🎨 Milla Design Bot

**Assistente de Demandas 24/7 - Monitora Notion, Trello e Drive Automaticamente**

---

## 📋 O que o Bot Faz

### ✅ Funcionalidades Principais

**1. Notificação Automática**
- 🔔 Monitora Notion continuamente (a cada 1 hora)
- 📢 Detecta novas demandas automaticamente
- 💬 Envia notificação no Telegram com:
  - Cliente
  - Demanda
  - Copy completa
  - Link para Notion

**2. Distribuição Inteligente**
- 🎨 Distribui para Designer 1 (Clarysse) ou Designer 2 (Larissa)
- 🎥 Distribui vídeos para Bruno (Editor)
- ✅ Você pode fazer a demanda você mesma
- 📅 Escolhe data de entrega (Hoje, Amanhã, ou calendário)

**3. Criação Automática de Cartões**
- 🏷️ Cria cartão no Trello automaticamente
- 📝 Com título, descrição e copy completa
- 🔗 Com link para Notion
- 📅 Com data de entrega e alarme
- 👤 Com designer atribuída
- 🏷️ Com labels automáticos

**4. Detecção de Alterações**
- 📝 Detecta quando uma demanda é alterada no Notion
- 🔄 Identifica automaticamente qual cartão do Trello é a alteração
- 📌 Move para coluna "Alterações"
- 💬 Adiciona comentário com o que precisa alterar
- 🔔 Notifica a designer no Telegram

**5. Gerenciamento de Prazos**
- ⏰ Alerta quando prazo está chegando
- 📊 Resumo diário de demandas
- 🎯 Visão semanal completa

---

## 🚀 Como Instalar

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/milla-bot.git
cd milla-bot
```

### Passo 2: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 3: Configurar Credenciais
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### Passo 4: Executar o Bot
```bash
python bot.py
```

---

## 🔑 Configuração de Credenciais

### Telegram
1. Crie um bot no [@BotFather](https://t.me/botfather)
2. Copie o token
3. Coloque em `TELEGRAM_TOKEN` no `.env`
4. Seu chat ID em `TELEGRAM_CHAT_ID`

### Trello
1. Vá para https://trello.com/app-key
2. Copie sua API Key
3. Gere um Token
4. Coloque em `TRELLO_API_KEY` e `TRELLO_TOKEN`

### Google Drive (Opcional)
1. Crie um projeto no Google Cloud
2. Gere credenciais de Service Account
3. Salve em `config/service_account.json`

---

## 📱 Como Usar

### Comandos Disponíveis

```
/start      - Mensagem de boas-vindas
/resumo     - Status geral de tudo
/hoje       - Demandas de hoje
/semana     - Visão da semana
/ajuda      - Ver todos os comandos
```

### Fluxo Completo

**1. Nova Demanda Detectada**
```
🔔 Nova Demanda!
👤 Cliente: XPTO Boutique
📝 Demanda: Criar 3 posts para Instagram
💬 Copy completa: [...]
🔗 Link: [Abrir no Notion]

[🎨 Design] [🎥 Vídeo] [✅ Fazer Eu] [❌ Ignorar]
```

**2. Você Clica em [🎨 Design]**
```
Para qual designer?
[🎨 Clarysse] [🎨 Larissa]
```

**3. Você Escolhe Clarysse**
```
Data de entrega?
[📅 Segunda 05/02] [📅 Terça 06/02] [...]
```

**4. Bot Confirma**
```
✅ Cartão criado!
🎨 Quadro: Designer 1
📅 Entrega: 06/02/2026
🔗 Ver no Trello
```

---

## 📊 Estrutura do Projeto

```
milla-bot/
├── bot.py                 # Arquivo principal
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de configuração
├── .gitignore            # Arquivos a ignorar
├── README.md             # Este arquivo
└── bot.log              # Logs do bot
```

---

## 🔧 Configurações Importantes

### URLs do Notion (Já Configuradas)
- Design 1: https://www.notion.so/Design-13d4d6b95fc78199a47cc62cb6a98aa9
- Design 2: https://www.notion.so/Design-19939a15596d81d9a1a2f155bca31f11
- Design 3: https://www.notion.so/Design-240fa1fd0b3a814c872cff12f9870186

### URLs do Trello (Já Configuradas)
- Minhas Demandas: https://trello.com/b/yb7AHMQ8/minhas-demandas
- Área do Convidado: https://trello.com/u/millamarttins961/boards

### Designers
- **Clarysse**: Designer 1
- **Larissa**: Designer 2
- **Bruno**: Editor de Vídeos

---

## 📈 Monitoramento

### Notion
- Verifica a cada **1 hora**
- Detecta novas demandas (sem etiqueta ou com "Nova")
- Detecta alterações (com etiqueta "Correção" ou "Alteração")

### Trello
- Verifica a cada **5 minutos**
- Monitora todos os quadros de designers
- Detecta cartões movidos para "Pronto"

---

## 🐛 Troubleshooting

### Bot não inicia
```bash
# Verificar erros
python bot.py

# Ver logs
tail -f bot.log
```

### Notificações não chegam
- Verifique `TELEGRAM_TOKEN`
- Verifique `TELEGRAM_CHAT_ID`
- Certifique-se de que o bot está no seu chat

### Trello não sincroniza
- Verifique `TRELLO_API_KEY` e `TRELLO_TOKEN`
- Certifique-se de que tem acesso aos quadros

---

## 📝 Logs

Os logs são salvos em `bot.log`. Para ver em tempo real:
```bash
tail -f bot.log
```

---

## 🤝 Suporte

Se encontrar problemas:
1. Verifique os logs em `bot.log`
2. Verifique as credenciais em `.env`
3. Abra uma issue no GitHub

---

## 📄 Licença

Este projeto é de uso pessoal.

---

**Desenvolvido com ❤️ para gerenciar suas demandas de design**
