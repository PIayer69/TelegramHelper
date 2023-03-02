import logging
import datetime
import pickle
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from weather import Weather

TOKEN = open("TOKEN.txt", "r").read().strip()
FILENAME_JOBS = "jobs"
w = Weather()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def initJobs(app):
    try:
        with open(FILENAME_JOBS, "rb") as f:
            jobs = pickle.load(f)
        for job in jobs:
            time = job["time"].time()
            app.job_queue.run_daily(
                greeting,
                chat_id=job["chat_id"],
                time=job["time"].time(),
                name=str(job["chat_id"]),
                data=job["city"],
            )
    except FileNotFoundError:
        return []


def saveJobs(jobsData) -> None:
    jobs = []
    for job in jobsData:
        jobs.append({"chat_id": job.chat_id, "time": job.next_t, "city": job.data})
    with open(FILENAME_JOBS, "wb+") as f:
        pickle.dump(jobs, f)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
        saveJobs(context.job_queue.jobs())
    return True


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = (
        "Timer successfully cancelled!" if job_removed else "You have no active timer."
    )
    await update.message.reply_text(text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="/pogoda [teraz/0 - dzisiaj/1 - jutro/2 - pojutrze] miasto",
    )


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args[0] == "teraz":
        weather = w.getCurrentWeather(
            context.args[1], "pl" if len(context.args) == 2 else context.args[2]
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=weather)
    else:
        forecastData = w.getForecast(context.args[1], "pl")
        dayForecast = w.findForecastByDay(
            forecastData, datetime.datetime.now().day + int(context.args[0])
        )
        forecast = w.prepareForecast(dayForecast, context.args[1])

        await context.bot.send_message(chat_id=update.effective_chat.id, text=forecast)


async def setGreeting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    if (
        len(context.args) == 2
        and type(context.args[0]) is str
        and all([h.isdigit() for h in context.args[1].split(":")])
    ):
        time = context.args[1].split(":")
        city = context.args[0]
        a = int(time[1])
        hour = datetime.time(
            int(context.args[1]) - 1 if len(time) == 1 else int(time[0]) - 1,
            0 if len(time) == 1 else int(time[1]),
        )

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_daily(
            greeting, hour, chat_id=chat_id, name=str(chat_id), data=city
        )

        text = "Ustawiono nowy greeting!"
        if job_removed:
            text += " Poprzedni usunięty."
        saveJobs(context.job_queue.jobs())
        await update.effective_message.reply_text(text)

    else:
        await update.effective_message.reply_text(
            "Użycie: /greeting <miasto> <godzina(1-24)>"
        )


async def greeting(context: ContextTypes.DEFAULT_TYPE):
    forecastData = w.getForecast(context.job.data, "pl")
    forecastDay = w.findForecastByDay(forecastData, datetime.datetime.now().day)
    forecast = w.prepareForecast(forecastDay, context.job.data)

    await context.bot.send_message(chat_id=context.job.chat_id, text=forecast)


async def jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = "\n".join([f"{j.chat_id}: {j.next_t.strftime('%H:%M')} + 1:00 {j.data}" for j in context.job_queue.jobs()])
    await context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text=jobs
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()
    initJobs(application)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pogoda", weather))
    application.add_handler(CommandHandler("greeting", setGreeting))
    application.add_handler(CommandHandler("jobs", jobs))

    application.run_polling()
