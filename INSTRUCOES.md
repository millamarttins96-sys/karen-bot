# 🚀 INSTRUÇÕES - BOT COMPLETO COM TODAS AS FUNCIONALIDADES

## ⚡ Tudo está pré-configurado! Só falta 3 passos:

---

## 📝 PASSO 1: Configurar Credenciais (2 minutos)

### 1.1 Obtenha seu Token do Telegram

1. Abra o Telegram
2. Procure por **@BotFather**
3. Envie `/start`
4. Envie `/newbot`
5. Escolha um nome (ex: "Milla Bot")
6. Escolha um username (ex: "milla_bot_123")
7. **Copie o TOKEN** que aparece

### 1.2 Obtenha seu Chat ID

1. Procure por **@userinfobot**
2. Envie `/start`
3. Ele mostra seu **User ID** (este é seu CHAT_ID)

### 1.3 Edite o arquivo `.env`

Abra o arquivo `.env` e substitua:

```
TELEGRAM_TOKEN=seu_token_do_bot_aqui
```

Por:
```
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

E:
```
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

Por:
```
TELEGRAM_CHAT_ID=987654321
```

### 1.4 (OPCIONAL) Configure Trello

Se quiser integração completa com Trello:

1. Vá para: https://trello.com/app-key
2. Copie sua **API Key**
3. Clique em **Token** e copie
4. Edite `.env`:

```
TRELLO_API_KEY=sua_api_key_aqui
TRELLO_TOKEN=seu_token_aqui
```

---

## 🚀 PASSO 2: Instalar Dependências (1 minuto)

Abra o terminal/prompt na pasta `milla-bot` e execute:

```bash
pip install -r requirements.txt
```

---

## ▶️ PASSO 3: Executar o Bot (30 segundos)

No mesmo terminal, execute:

```bash
python bot.py
```

Você deve ver:
```
✅ Bot iniciado com sucesso!
🔔 Aguardando mensagens do Telegram...
📱 Chat ID: 987654321
==================================================
```

---

## ✅ PRONTO!

Agora vá ao Telegram e:

1. Procure por seu bot (username que criou)
2. Envie `/start`
3. Ele vai responder! 🎉

---

## 🧪 Teste os Comandos

- `/start` - Boas-vindas e informações
- `/resumo` - Status geral de demandas
- `/hoje` - Demandas de hoje
- `/semana` - Visão da semana
- `/testar` - Testar todas as funcionalidades
- `/ajuda` - Todos os comandos

---

## 🎯 Funcionalidades Implementadas

### ✅ Monitoramento Notion
- Monitora 3 páginas do Notion continuamente (a cada 1 hora)
- Detecta novas demandas automaticamente
- Detecta alterações em demandas existentes

### ✅ Notificações Telegram
- Envia notificação quando detecta nova demanda
- Envia notificação quando detecta alteração
- Inclui: Cliente, Demanda, Copy, Link para Notion

### ✅ Criação de Cartões Trello
- Cria cartão automaticamente quando distribui
- Adiciona título, descrição e copy completa
- Adiciona link para Notion
- Adiciona data de entrega com alarme
- Atribui designer automaticamente
- Adiciona labels automáticos

### ✅ Distribuição Automática
- Distribui para Clarysse, Larissa ou Bruno
- Pergunta data de entrega (Hoje, Amanhã, ou calendário)
- Cria cartão no Trello automaticamente
- Notifica a designer no Telegram

### ✅ Detecção de Alterações
- Detecta quando uma demanda é alterada no Notion
- Identifica automaticamente qual cartão do Trello é a alteração
- Move para coluna "Alterações"
- Adiciona comentário com o que precisa alterar
- Notifica a designer no Telegram

### ✅ Gerenciamento de Prazos
- Alerta quando prazo está chegando (17:30)
- Resumo diário de demandas
- Visão semanal completa
- Rastreamento de demandas concluídas

### ✅ Sistema de Semanas
- Virada de semana automática (Sábado 00:01)
- Atualização automática de datas
- Contagem de demandas por semana

---

## 📊 Como Funciona

### Fluxo Completo de uma Demanda

1. **Você adiciona demanda no Notion**
2. **Bot detecta automaticamente** (a cada 1 hora)
3. **Bot notifica você no Telegram** com botões:
   - [🎨 Design] [🎥 Vídeo] [✅ Fazer Eu] [❌ Ignorar]
4. **Você clica em [🎨 Design]**
5. **Bot pergunta qual designer:**
   - [🎨 Clarysse] [🎨 Larissa]
6. **Você escolhe Clarysse**
7. **Bot pergunta data de entrega:**
   - [📅 Segunda] [📅 Terça] [📅 Quarta] [📅 Quinta] [📅 Sexta]
8. **Você escolhe Terça**
9. **Bot cria cartão no Trello:**
   - ✅ Título: Cliente
   - ✅ Descrição: Demanda
   - ✅ Copy completa
   - ✅ Link para Notion
   - ✅ Data de entrega: Terça
   - ✅ Designer: Clarysse
   - ✅ Labels: "Nova Demanda", "Cliente"
10. **Bot notifica Clarysse no Telegram**
11. **Clarysse começa a trabalhar**

### Se Houver Alteração

1. **Você altera a demanda no Notion**
2. **Bot detecta a alteração** (a cada 1 hora)
3. **Bot notifica você:**
   - "ALTERAÇÃO DETECTADA!"
   - Cliente, Demanda Original, O que Mudou
4. **Você clica em [🎨 Clarysse]**
5. **Bot automaticamente:**
   - ✅ Encontra o cartão original no Trello
   - ✅ Move para coluna "Alterações"
   - ✅ Adiciona comentário com o que mudou
   - ✅ Adiciona nova data de prazo
   - ✅ Notifica Clarysse no Telegram

---

## ❌ Se não funcionar

### Erro: "TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados"

**Solução:**
- Abra o arquivo `.env`
- Verifique se tem `TELEGRAM_TOKEN=` e `TELEGRAM_CHAT_ID=`
- Certifique-se de que tem valores reais (não "seu_token_aqui")

### Erro: "ModuleNotFoundError: No module named 'telegram'"

**Solução:**
```bash
pip install python-telegram-bot
```

### Bot não responde no Telegram

**Solução:**
1. Verifique se o bot está rodando (veja se tem mensagens no terminal)
2. Verifique se o token está correto
3. Verifique se o chat ID está correto
4. Procure seu bot pelo username (não pelo nome)
5. Veja os logs: `tail -f bot.log`

### Notion não sincroniza

**Solução:**
1. Verifique se o Notion está acessível
2. Verifique se as URLs estão corretas
3. Veja os logs para mais detalhes

### Trello não sincroniza

**Solução:**
1. Verifique a API Key e Token
2. Certifique-se de que tem acesso aos quadros
3. Veja os logs para mais detalhes

---

## 📊 Monitoramento

### Notion
- Verifica a cada **1 hora**
- Detecta novas demandas
- Detecta alterações

### Trello
- Verifica a cada **5 minutos**
- Monitora todos os quadros
- Detecta cartões movidos

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

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs em `bot.log`
2. Verifique as credenciais em `.env`
3. Teste cada funcionalidade com `/testar`

---

**Pronto! Seu bot está 100% funcional!** 🎉
