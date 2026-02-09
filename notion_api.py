import os
from notion_client import Client
from app.storage.db import kv_get, kv_set

def notion_client():
    token = os.getenv("NOTION_TOKEN","").strip()
    if not token:
        return None
    return Client(auth=token)

def fetch_recent_from_db(db_id: str, since_iso: str | None):
    nc = notion_client()
    if not nc or not db_id:
        return []
    # Notion filter: last_edited_time > since
    filt = None
    if since_iso:
        filt = {"timestamp":"last_edited_time","last_edited_time":{"after": since_iso}}
    res = nc.databases.query(database_id=db_id, filter=filt, page_size=20)
    return res.get("results", [])

def extract_simple(page: dict, mapping: dict):
    props = page.get("properties",{})
    out = {}
    # mapping: field -> property_name
    for k, prop_name in mapping.items():
        p = props.get(prop_name)
        if not p: 
            out[k] = ""
            continue
        t = p.get("type")
        if t == "title":
            out[k] = "".join([x.get("plain_text","") for x in p["title"]])
        elif t == "rich_text":
            out[k] = "".join([x.get("plain_text","") for x in p["rich_text"]])
        elif t == "date":
            d = p["date"]
            out[k] = d["start"] if d else ""
        elif t == "select":
            s = p["select"]
            out[k] = s["name"] if s else ""
        else:
            out[k] = str(p.get(t,""))
    out["url"] = page.get("url","")
    out["last_edited_time"] = page.get("last_edited_time","")
    out["id"] = page.get("id","")
    return out
