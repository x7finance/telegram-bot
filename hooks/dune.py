from telegram import *
from telegram.ext import *

import os, requests
from datetime import datetime

from constants import urls


API_KEY = os.getenv("DUNE_API_KEY")
HEADER = {"x-dune-api-key": API_KEY}
BASE_URL = "https://api.dune.com/api/v1/"

TOP_PAIRS_ID = "2970801"
VOLUME_ID = "2972368"
TIME_ALLOWED = 6 * 60 * 60

VOLUME_TEXT = ""
VOLUME_FLAG = False
VOLUME_TIMESTAMP = datetime.now().timestamp()
VOLUME_LAST_DATE = datetime.fromtimestamp(VOLUME_TIMESTAMP).strftime("%Y-%m-%d %H:%M:%S")

TRENDING_TEXT = {}
TRENDING_FLAG = {}
TRENDING_TIMESTAMP = {}
TRENDING_LAST_DATE = {}


def make_api_url(module, action, identifier):
    return f"{BASE_URL}{module}/{identifier}/{action}"


def execute_query(query_id, engine="small"):
    response = requests.post(
        make_api_url("query", "execute", query_id),
        headers=HEADER,
        params={"performance": engine},
    )
    return response.json()["execution_id"]


def get_query_status(execution_id):
    return requests.get(make_api_url("execution", "status", execution_id), headers=HEADER)


def get_query_results(execution_id):
    return requests.get(make_api_url("execution", "results", execution_id), headers=HEADER)


def cancel_query_execution(execution_id):
    return requests.get(make_api_url("execution", "cancel", execution_id), headers=HEADER)


async def get_error(update: Update, context: ContextTypes.DEFAULT_TYPE, call_type):
        await update.message.reply_text(
            f'*{call_type}*\n\nUnable to get Dune data, please use the link below',
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="X7 Dune Dashboard", url=f"{urls.DUNE}"
                        )
                    ],
                ]
            ),
        )

