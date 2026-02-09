def format_new_demand_message(d):
    client = d.get("client","(sem cliente)")
    title = d.get("title","(sem título)")
    demand = d.get("demand","")
    copy = d.get("copy","")
    link = d.get("link","")
    src = d.get("source","")
    return (
        "🔔 *Nova Demanda!*\n\n"
        f"👤 Cliente: *{client}*\n"
        f"📝 Demanda: {title}\n\n"
        f"💬 Copy:\n{copy[:1200]}\n\n"
        f"🔗 Link: {link}\n"
        f"📌 Fonte: {src}"
    )

def format_status_message(events):
    if not events:
        return "Sem nada por aqui ainda."
    lines = ["📊 *Status (últimos eventos)*\n"]
    for ts, source, kind, client, title, payload in events:
        c = f" — {client}" if client else ""
        t = f" — {title}" if title else ""
        lines.append(f"• {ts[:19]} | {source}:{kind}{c}{t}")
    return "\n".join(lines)
