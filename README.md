# MillaDesign Bot (Telegram + Trello + Notion + Drive)

Este repositório é um **MVP pronto pra subir no GitHub** com a estrutura do bot do seu documento:
- Notifica novas demandas (Trello/Notion) no Telegram
- Botões: 🎨 Design / 🎥 Vídeo / ✅ Fazer Eu / ❌ Ignorar
- Delegar pra **Designer Clarysse**, **Designer Larissa** ou **Editor Bruno**
- Escolher **data de entrega** (Hoje / Amanhã / Escolher)
- Criar cartão no Trello com descrição padrão, label e prazo
- Detectar **Alteração/Correção** e mover para lista 🔄 Alterações (quando encontrar o card)
- Virada de semana (renomeia listas com datas) via comando
- Upload automático no **Google Drive** (service account) para demandas aprovadas
- Dashboard web simples (abas: Você, Clarysse, Larissa, Bruno)

> ⚠️ Segurança: **NÃO** commite tokens/senhas. Use `.env` (não versionado).
> Se você já colocou tokens em PDF/prints, **gire (regenere) tudo**.

---

## 1) Como rodar (modo simples)

### Requisitos
- Python 3.11+
- Uma máquina ligada (ou Render/Railway/Fly.io/VPS)

### Instalar
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

### Configurar `.env`
Preencha:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID` (seu chat ou grupo)
- `TRELLO_KEY` e `TRELLO_TOKEN`
- IDs dos quadros/listas do Trello
- (Opcional) Notion: `NOTION_TOKEN` + `NOTION_DB_*`
- (Opcional) Drive: dados do service account JSON + pastas raiz por cliente

### Rodar
```bash
python -m app.main
```

---

## 2) Central de comando (Telegram)
Comandos:
- `/ajuda`
- `/resumo`
- `/hoje`
- `/semana`
- `/clarysse`
- `/larissa`
- `/bruno`
- `/add_cliente NOME`
- `/remove_cliente NOME`
- `/virar_semana`

---

## 3) O que você precisa me passar pra ficar 100% redondo
Esse MVP roda, mas pra “colar perfeito” no seu Trello/Notion você vai preencher no `.env`:
- ID dos **4 quadros** (Você, Clarysse, Larissa, Bruno)
- ID das listas padrão (📥 Novas, 🔄 Alterações, e as listas do calendário)
- Regras de cada página do Notion (campos exatos: título, cliente, data, copy)

---

## 4) Deploy (24h)
- Recomendo: **Render** (web service) ou **Railway**.
- Esse projeto roda em **polling** (sem webhook), então é fácil.

---

## 5) Estrutura
- `app/bot/` Telegram (botões, comandos)
- `app/integrations/` Trello, Notion, Drive
- `app/jobs/` monitoramento + rotinas (virada de semana, alertas)
- `app/web/` dashboard (FastAPI)
- `app/storage/` SQLite (estado/cursor)

Boa!
