import os, re, requests
from datetime import datetime, time
from pytz import timezone
from app.storage.db import kv_get, kv_set

TRELLO = os.getenv("TRELLO_BASE_URL","https://api.trello.com/1")
KEY = os.getenv("TRELLO_KEY","")
TOKEN = os.getenv("TRELLO_TOKEN","")
TZ = timezone(os.getenv("TIMEZONE","America/Sao_Paulo"))

BOARD_ENV = {
    "milla": "BOARD_MILLA",
    "clarysse": "BOARD_CLARYSSE",
    "larissa": "BOARD_LARISSA",
    "bruno": "BOARD_BRUNO",
}

def _params(extra=None):
    p = {"key": KEY, "token": TOKEN}
    if extra: p.update(extra)
    return p

def _get(url, params=None):
    r = requests.get(url, params=_params(params), timeout=30)
    r.raise_for_status()
    return r.json()

def _post(url, data=None):
    r = requests.post(url, params=_params(), data=data or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def _put(url, data=None):
    r = requests.put(url, params=_params(), data=data or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def get_board_id(who: str):
    env = BOARD_ENV.get(who)
    if not env:
        raise ValueError("who inválido")
    bid = os.getenv(env,"").strip()
    if not bid:
        raise RuntimeError(f"Faltou {env} no .env")
    return bid

def lists_on_board(board_id: str):
    return _get(f"{TRELLO}/boards/{board_id}/lists", {"fields":"name,closed"})

def find_list_id(board_id: str, name_contains: str):
    for lst in lists_on_board(board_id):
        if lst.get("closed"): 
            continue
        if name_contains.lower() in lst["name"].lower():
            return lst["id"]
    return None

def find_weekday_list_id(board_id: str, due_date):
    # tenta achar lista que tenha o DD/MM do prazo
    target = due_date.strftime("%d/%m")
    for lst in lists_on_board(board_id):
        if lst.get("closed"): 
            continue
        if target in lst["name"]:
            return lst["id"]
    # fallback: inbox
    return find_list_id(board_id, os.getenv("LIST_INBOX_NAME","Novas"))

def create_task_card(who: str, task_type: str, due_date, demand: dict):
    board_id = get_board_id(who)
    list_id = find_weekday_list_id(board_id, due_date)

    # prazo 17:30 (config)
    dh = int(os.getenv("DEADLINE_HOUR","17"))
    dm = int(os.getenv("DEADLINE_MINUTE","30"))
    due_dt = datetime.combine(due_date, time(dh, dm)).astimezone(TZ)

    title = demand.get("client","Demanda")
    desc = (
        f"📝 DEMANDA:\n{demand.get('title','')}\n\n"
        f"💬 COPY COMPLETA:\n{demand.get('copy','')}\n\n"
        f"🔗 TAREFA ORIGINAL:\n{demand.get('link','')}\n"
    )

    card = _post(f"{TRELLO}/cards", {
        "idList": list_id,
        "name": title,
        "desc": desc[:15000],
        "due": due_dt.isoformat(),
    })
    return {"id": card["id"], "url": card.get("url")}

def list_cards(board_id: str):
    return _get(f"{TRELLO}/boards/{board_id}/cards", {"fields":"name,desc,url,idList,dateLastActivity", "filter":"open"})

def find_best_match_card(who: str, client: str, keywords: list[str]):
    # MVP: match por título + palavras-chave na desc
    board_id = get_board_id(who)
    cards = list_cards(board_id)
    best = None
    best_score = 0
    for c in cards:
        score = 0
        if client and client.lower() in (c["name"] or "").lower():
            score += 2
        desc = (c.get("desc") or "").lower()
        for kw in keywords:
            if kw and kw.lower() in desc:
                score += 1
        if score > best_score:
            best_score = score
            best = c
    return best

def move_to_changes(who: str, card_id: str):
    board_id = get_board_id(who)
    changes_name = os.getenv("LIST_CHANGES_NAME","Alterações")
    list_id = find_list_id(board_id, changes_name) or find_list_id(board_id, "alter")
    if not list_id:
        raise RuntimeError(f"Não achei a lista de alterações no quadro {who}. Crie uma lista chamada: {changes_name}")
    _put(f"{TRELLO}/cards/{card_id}", {"idList": list_id})
    return True

def rename_week_lists():
    # Renomeia listas Segunda..Sexta seguindo o padrão do PDF.
    # MVP: só renomeia se encontrar "(DD/MM)" no nome.
    import datetime as dt
    res = []
    for who, env in BOARD_ENV.items():
        board_id = os.getenv(env,"").strip()
        if not board_id:
            continue
        lists = lists_on_board(board_id)
        # achar uma data base (segunda atual)
        today = dt.datetime.now(TZ).date()
        # próxima segunda
        monday = today + dt.timedelta(days=(7 - today.weekday()) % 7) if today.weekday()!=0 else today
        # se hoje é sexta/sábado/domingo, pula pra próxima segunda
        if today.weekday() >= 4:
            monday = today + dt.timedelta(days=(7 - today.weekday()))
        mapping = {
            "Segunda": monday,
            "Terça": monday + dt.timedelta(days=1),
            "Quarta": monday + dt.timedelta(days=2),
            "Quinta": monday + dt.timedelta(days=3),
            "Sexta": monday + dt.timedelta(days=4),
        }
        for lst in lists:
            name = lst["name"]
            for day, date_ in mapping.items():
                if day.lower() in name.lower():
                    new_name = re.sub(r"\(\d{2}/\d{2}.*?\)", f"({date_.strftime('%d/%m')})", name)
                    if new_name == name and "(" not in name:
                        new_name = f"{day}-Feira ({date_.strftime('%d/%m')})"
                    _put(f"{TRELLO}/lists/{lst['id']}", {"name": new_name})
                    break
        res.append(f"✅ Atualizei listas do quadro: {who}")
    return "\n".join(res) if res else "⚠️ Não achei quadros no .env."
