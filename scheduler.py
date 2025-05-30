from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from main1 import main
from agents.draft_checker import check_drafts_for_compliance
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def scheduled_job():
    logging.info("Running scheduled compliance check...")
    check_drafts_for_compliance()
    logging.info("Completed compliance check.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(
        scheduled_job,
        trigger=IntervalTrigger(minutes=1),
        id="email_compliance_check",
        name="Check emails every 5 minutes",
        replace_existing=True
    )
    
    check_drafts_for_compliance()
    # scheduled_job()

    try:
        logging.info("Scheduler started. Press Ctrl+C to stop.")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")