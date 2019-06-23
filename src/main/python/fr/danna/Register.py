# import urllib
from datetime import datetime
from enum import Enum

import pytz as pytz
import requests
from dataclasses import dataclass
from requests import Response

CUSTOMER_ACCOUNT_ID = 'annick.danna@gmail.com'
CUSTOMER_ACCOUNT_PWD = 'Resamania2019'
CUSTOMER_CLIENT_ID = '4_5pq41l35lao848k44kk84ssc8kgkcswo0s0k040cwkgw4ko8g4'
CUSTOMER_CLIENT_SECRET = '1qnd586ifbesc4444cc0o8g4sw4g4kwcco0owg8o4ccg48ssog'


@dataclass
class Session:
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str


def login(user_id: str, user_pwd: str, client_id, client_secret) -> Session:
    """
    Logs in (authent) the given user.
    :param client_id:
    :param client_secret:
    :param client_id:
    :param client_secret:
    """
    url = 'https://api.fr.fitnesspark.app/fitnesspark/oauth/v2/token'
    headers = {
        'Referer': 'https://member.fr.fitnesspark.app/fitnesspark/',
        'Origin': 'https://member.fr.fitnesspark.app',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/75.0.3770.90 Chrome/75.0.3770.90 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    }
    data = {
        'grant_type': 'password',
        'username': user_id,
        'password': user_pwd,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'https://member.fr.fitnesspark.app/fitnesspark/',
    }
    resp: Response = requests.post(url, headers=headers, data=data)
    if resp.status_code != requests.codes.ok:
        raise Exception("Can't fetch URL: {0}".format(resp.status_code))
    respDict = resp.json()
    user_session = Session(
        respDict['access_token'],
        respDict['expires_in'],
        respDict['refresh_token'],
        respDict['scope'],
        respDict['token_type']
    )
    return user_session


class Activity(Enum):
    ZUMBA = 1
    CAF = 2
    TBC = 3
    CROSS_TRAINING = 4


def register(session: Session, activity: Activity, date: datetime):
    """
    Register the user of the given session to the given activity, at the given date.
    """
    pass


FRANCE_TZ = pytz.timezone('Europe/Paris')

session: Session = login(CUSTOMER_ACCOUNT_ID, CUSTOMER_ACCOUNT_PWD, CUSTOMER_CLIENT_ID, CUSTOMER_CLIENT_SECRET)

register(session, Activity.CROSS_TRAINING, datetime(2019, 7, 7, 11, 0, 0, 0, FRANCE_TZ))
