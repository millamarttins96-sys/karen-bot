# 🔧 Guia de Instalação e Setup

Siga este guia para configurar o bot do zero!

---

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta no Telegram
- Conta no Trello
- Conta no Notion
- Conta no Google Drive (opcional)

---

## 🚀 Passo 1: Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/milla-bot.git
cd milla-bot
```

---

## 📦 Passo 2: Instalar Dependências

### No Windows:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### No Mac/Linux:
```bash
pip3 install -r requirements.txt
```

---

## 🔑 Passo 3: Configurar Telegram

### 3.1 Criar um Bot no Telegram

1. Abra o Telegram
2. Procure por **@BotFather**
3. Envie `/start`
4. Envie `/newbot`
5. Escolha um nome (ex: "Milla Design Bot")
6. Escolha um username (ex: "milla_design_bot")
7. **Copie o TOKEN** que aparece

### 3.2 Obter seu Chat ID

1. Procure por **@userinfobot**
2. Envie `/start`
3. Ele vai mostrar seu **User ID** (este é seu CHAT_ID)

### 3.3 Adicionar ao .env

Edite o arquivo `.env`:
```
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

---

## 🎯 Passo 4: Configurar Trello

### 4.1 Obter API Key

1. Vá para: https://trello.com/app-key
2. Copie a **API Key**
3. Clique em **Token** (no mesmo link)
4. Copie o **Token**

### 4.2 Adicionar ao .env

```
TRELLO_API_KEY=sua_api_key_aqui
TRELLO_TOKEN=seu_token_aqui
```

---

## 📝 Passo 5: Configurar Notion (Automático)

As URLs do Notion já estão configuradas no código:

- Design 1: https://www.notion.so/Design-13d4d6b95fc78199a47cc62cb6a98aa9
- Design 2: https://www.notion.so/Design-19939a15596d81d9a1a2f155bca31f11
- Design 3: https://www.notion.so/Design-240fa1fd0b3a814c872cff12f9870186

---

## 🚀 Passo 6: Executar o Bot

```bash
python bot.py
```

Você deve ver:
```
2026-02-09 10:00:00 - root - INFO - Bot iniciado com sucesso!
```

---

## ✅ Passo 7: Testar

1. Vá ao Telegram
2. Procure por seu bot (username que criou)
3. Envie `/start`
4. Você deve receber uma mensagem de boas-vindas

---

## 🔧 Configuração Avançada (Opcional)

### Google Drive

Se quiser usar upload automático para Google Drive:

1. Vá para: https://console.cloud.google.com
2. Crie um novo projeto
3. Ative a API do Google Drive
4. Crie credenciais (Service Account)
5. Baixe o JSON
6. Salve em `config/service_account.json`
7. Configure em `.env`:

```
GOOGLE_DRIVE_FOLDER_ID=seu_folder_id_aqui
GOOGLE_SERVICE_ACCOUNT_JSON=config/service_account.json
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'telegram'"

**Solução:**
```bash
pip install python-telegram-bot
```

### Erro: "TELEGRAM_TOKEN not found"

**Solução:**
- Verifique se o arquivo `.env` existe
- Verifique se tem `TELEGRAM_TOKEN=...` dentro
- Certifique-se de que não tem espaços extras

### Bot não responde no Telegram

**Solução:**
1. Verifique se o bot está rodando (`python bot.py`)
2. Verifique se o token está correto
3. Verifique se o chat ID está correto
4. Veja os logs: `tail -f bot.log`

### Trello não sincroniza

**Solução:**
1. Verifique a API Key e Token
2. Certifique-se de que tem acesso aos quadros
3. Verifique os nomes dos quadros

---

## 📊 Verificar Instalação

Para verificar se tudo está instalado corretamente:

```bash
python -c "import telegram; print('Telegram OK')"
python -c "import trello; print('Trello OK')"
python -c "import requests; print('Requests OK')"
python -c "import dotenv; print('Dotenv OK')"
```

---

## 🎯 Próximos Passos

1. ✅ Instalar dependências
2. ✅ Configurar Telegram
3. ✅ Configurar Trello
4. ✅ Executar o bot
5. ✅ Testar no Telegram
6. 📈 Monitorar logs
7. 🚀 Deixar rodando 24/7

---

## 🔄 Manter Rodando 24/7

### Opção 1: Usar Screen (Linux/Mac)

```bash
screen -S milla-bot
python bot.py
# Pressione Ctrl+A depois D para sair
```

Para voltar:
```bash
screen -r milla-bot
```

### Opção 2: Usar Systemd (Linux)

Crie arquivo `/etc/systemd/system/milla-bot.service`:

```ini
[Unit]
Description=Milla Design Bot
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/milla-bot
ExecStart=/usr/bin/python3 /caminho/para/milla-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Depois:
```bash
sudo systemctl start milla-bot
sudo systemctl enable milla-bot
```

### Opção 3: Usar Heroku (Cloud)

1. Crie conta em https://www.heroku.com
2. Crie um arquivo `Procfile`:
```
worker: python bot.py
```
3. Faça deploy:
```bash
heroku login
heroku create seu-app-name
git push heroku main
```

---

**Pronto! Seu bot está configurado!** 🎉
