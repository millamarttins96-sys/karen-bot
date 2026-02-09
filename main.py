import os
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app.storage.db import init_db
from app.bot.telegram_bot import build_application
from app.jobs.trello_watch import trello_poll_job
from app.jobs.notion_watch import notion_poll_job
from app.jobs.deadline_alerts import deadline_alerts_job
from app.web.server import create_web_app

import uvicorn
import asyncio


async def run_bot():
    load_dotenv()
    init_db()

    app = build_application()

    # Scheduler
    tz = timezone(os.getenv("TIMEZONE","America/Sao_Paulo"))
    sched = AsyncIOScheduler(timezone=tz)
    sched.add_job(trello_poll_job, "interval", seconds=60, args=[app])
    sched.add_job(notion_poll_job, "interval", seconds=int(os.getenv("NOTION_POLL_SECONDS","120")), args=[app])
    sched.add_job(deadline_alerts_job, "cron", hour=int(os.getenv("DEADLINE_HOUR","17")), minute=int(os.getenv("DEADLINE_MINUTE","30")), args=[app])
    sched.start()

    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=["message","callback_query"])
    await app.updater.idle()


def run_dashboard():
    web_app = create_web_app()
    uvicorn.run(web_app, host="0.0.0.0", port=int(os.getenv("PORT","8000")))


if __name__ == "__main__":
    # Rodar bot + dashboard juntos (simples)
    # - Dashboard em http://localhost:8000
    # - Bot via polling
    loop = asyncio.get_event_loop()
    # Rodar dashboard em thread separada
    import threading
    t = threading.Thread(target=run_dashboard, daemon=True)
    t.start()
    loop.run_until_complete(run_bot())
