from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(generate_weekly_report, 'interval', weeks=1)
scheduler.start()
