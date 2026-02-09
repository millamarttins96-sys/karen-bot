import os, json, base64
from datetime import datetime
from pytz import timezone

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

TZ = timezone(os.getenv("TIMEZONE","America/Sao_Paulo"))

def _service():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","").strip()
    if not raw:
        return None
    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive","v3",credentials=creds, cache_discovery=False)

def root_map():
    raw = os.getenv("GOOGLE_DRIVE_ROOT_MAP_JSON","").strip()
    return json.loads(raw) if raw else {}

def month_name_pt(dt: datetime):
    meses = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    return meses[dt.month-1]

def _find_or_create_folder(svc, parent_id, name):
    q = f"'{parent_id}' in parents and name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    res = svc.files().list(q=q, fields="files(id,name)").execute()
    files = res.get("files",[])
    if files:
        return files[0]["id"]
    meta = {"name": name, "mimeType":"application/vnd.google-apps.folder", "parents":[parent_id]}
    f = svc.files().create(body=meta, fields="id,webViewLink").execute()
    return f["id"]

def upload_files_for_client(client_name: str, post_name: str, files: list[tuple[str, bytes]]):
    svc = _service()
    if not svc:
        raise RuntimeError("Drive não configurado (GOOGLE_SERVICE_ACCOUNT_JSON).")
    roots = root_map()
    root_id = roots.get(client_name)
    if not root_id:
        raise RuntimeError(f"Não achei pasta raiz do cliente no mapa: {client_name}")
    now = datetime.now(TZ)
    month_folder = _find_or_create_folder(svc, root_id, month_name_pt(now))
    post_folder = _find_or_create_folder(svc, month_folder, post_name)

    for filename, blob in files:
        media = MediaInMemoryUpload(blob, resumable=False)
        meta = {"name": filename, "parents":[post_folder]}
        svc.files().create(body=meta, media_body=media, fields="id").execute()

    link = svc.files().get(fileId=post_folder, fields="webViewLink").execute().get("webViewLink")
    return link
