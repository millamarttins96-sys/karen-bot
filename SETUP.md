# 🚀 Guia de Instalação e Setup

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta Telegram
- Chaves de API: Trello, Google Drive, Notion (opcional)

## Passo 1: Clonar ou Extrair o Repositório

### Opção A: Via Git

```bash
git clone https://github.com/seu-usuario/milla-bot.git
cd milla-bot
```

### Opção B: Extrair ZIP

```bash
unzip milla_bot_complete.zip
cd milla_bot
```

## Passo 2: Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

## Passo 4: Configurar Credenciais

### 4.1 Copiar arquivo de exemplo

```bash
cp config/.env.example config/.env
```

### 4.2 Preencher credenciais no `config/.env`

#### Telegram

1. Abra [@BotFather](https://t.me/botfather) no Telegram
2. Envie `/newbot`
3. Siga as instruções
4. Copie o token e adicione em `config/.env`:

```
TELEGRAM_TOKEN=seu_token_aqui
```

5. Para obter seu `TELEGRAM_CHAT_ID`:
   - Envie uma mensagem para seu bot
   - Acesse: `https://api.telegram.org/botSEU_TOKEN/getUpdates`
   - Procure por `"chat":{"id":NUMERO}`
   - Adicione em `config/.env`:

```
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

#### Trello

1. Acesse [Trello Developer](https://trello.com/app-key)
2. Copie a **API Key**
3. Clique em **Token** e gere um novo token
4. Adicione em `config/.env`:

```
TRELLO_API_KEY=sua_api_key
TRELLO_TOKEN=seu_token
```

#### Google Drive

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um novo projeto
3. Ative a API do Google Drive
4. Crie uma **Service Account**:
   - Vá para "Service Accounts"
   - Clique "Create Service Account"
   - Preencha os detalhes
   - Clique "Create and Continue"
5. Crie uma chave JSON:
   - Vá para a aba "Keys"
   - Clique "Add Key" → "Create new key"
   - Escolha "JSON"
   - Salve como `config/service_account.json`
6. Compartilhe suas pastas do Drive com o email da Service Account

#### Notion (Opcional)

1. Acesse [Notion Integrations](https://www.notion.so/my-integrations)
2. Crie uma nova integração
3. Copie o token e adicione em `config/.env`:

```
NOTION_TOKEN=seu_token
```

4. Compartilhe suas páginas com a integração

## Passo 5: Estruturar Quadros do Trello

O bot espera que seus quadros tenham a seguinte estrutura:

### Seu Quadro: "Minhas Demandas"

```
📥 Novas Demandas
🔄 Alterações
━━━━━━━━━━━━━━━━━━━━
📅 Segunda-Feira (DD/MM)
📅 Terça-Feira (DD/MM)
📅 Quarta-Feira (DD/MM)
📅 Quinta-Feira (DD/MM)
📅 Sexta-Feira (DD/MM)
```

### Quadros dos Designers

- Designer Clarysse
- Designer Larissa
- Editor Bruno

(Mesma estrutura de colunas)

## Passo 6: Executar o Bot

### Etapa 1 (Notificações e Distribuição)

```bash
python etapa1/main.py
```

### Etapa 2 (Automações)

Quando estiver pronto, integre os módulos da Etapa 2 ao `etapa1/main.py`.

### Etapa 3 (Extras)

Quando estiver pronto, integre os módulos da Etapa 3 e inicie o dashboard:

```bash
python etapa3/dashboard_app.py
```

## Passo 7: Verificar Funcionamento

1. **Telegram**: Envie `/start` para o bot
2. **Logs**: Verifique `logs/bot.log` para erros
3. **Notion**: Verifique se o bot está monitorando (a cada 1 hora)
4. **Trello**: Verifique se o bot está monitorando (a cada 5 minutos)

## Troubleshooting

### "ModuleNotFoundError: No module named 'telegram'"

Instale as dependências novamente:

```bash
pip install -r requirements.txt
```

### "TELEGRAM_TOKEN not found"

Verifique se o arquivo `config/.env` existe e tem o token correto.

### Bot não recebe mensagens

1. Verifique se o `TELEGRAM_TOKEN` está correto
2. Verifique se o `TELEGRAM_CHAT_ID` está correto
3. Envie uma mensagem para o bot no Telegram
4. Verifique os logs: `tail -f logs/bot.log`

### Notion não está sendo monitorado

1. Verifique se as URLs do Notion estão corretas
2. Verifique se você tem acesso às páginas
3. Aumentar intervalo de sincronização em `config/.env`

### Trello não está sendo monitorado

1. Verifique se as credenciais estão corretas
2. Verifique se os nomes dos quadros estão exatos
3. Verifique os logs: `tail -f logs/bot.log`

### Google Drive não funciona

1. Verifique se o arquivo `config/service_account.json` existe
2. Verifique se as pastas foram compartilhadas com o email da Service Account
3. Verifique os logs: `tail -f logs/drive.log`

## Configurações Avançadas

### Alterar Intervalo de Sincronização

Em `config/.env`:

```
NOTION_SYNC_INTERVAL=3600  # 1 hora em segundos
```

### Alterar Hora da Virada de Semana

Em `config/.env`:

```
WEEK_TURN_DAY=Saturday
WEEK_TURN_TIME=00:01
```

### Alterar Hora do Alerta de Prazo

Em `config/.env`:

```
WORK_END_TIME=17:30
```

## Deploy

Para fazer deploy em produção:

### Opção 1: Heroku

```bash
# Instalar Heroku CLI
# Fazer login
heroku login

# Criar app
heroku create seu-app-name

# Fazer deploy
git push heroku main
```

### Opção 2: AWS

1. Criar EC2 instance
2. Instalar Python
3. Clonar repositório
4. Configurar credenciais
5. Executar com `screen` ou `systemd`

### Opção 3: DigitalOcean

1. Criar Droplet
2. Instalar Python
3. Clonar repositório
4. Configurar credenciais
5. Usar PM2 para manter rodando

## Próximos Passos

1. ✅ Etapa 1: Notificações e Distribuição
2. 🔄 Etapa 2: Automações (integrar ao main.py)
3. 🎯 Etapa 3: Extras (integrar ao main.py)

## Suporte

Para reportar problemas ou sugestões, abra uma issue no GitHub.

---

**Desenvolvido com ❤️ para automatizar seu fluxo de trabalho**
