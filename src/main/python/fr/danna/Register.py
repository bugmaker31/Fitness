# import urllib
import json
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

FRANCE_TZ = pytz.timezone('Europe/Paris')


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
        raise Exception("Can't fetch URL: {0} {1}".format(resp.status_code, resp.content))
    resp_dict = resp.json()
    user_session = Session(
        resp_dict['access_token'],
        resp_dict['expires_in'],
        resp_dict['refresh_token'],
        resp_dict['scope'],
        resp_dict['token_type']
    )
    return user_session


class Activity(Enum):
    ZUMBA = 1
    CAF = 2
    TBC = 3
    BIKING = 4
    CROSS_TRAINING = 5


@dataclass
class Class:
    activity: Activity
    when: datetime
    id: int


def clazz(activity: Activity, when: datetime) -> Class:
    return Class(activity, when, 212429)


def register(session: Session, activity: Activity, when: datetime):
    """
    Register the user of the given session to the given activity, at the given date.
    """

    theClazz: Class = clazz(activity, datetime)

    url = 'https://api.fr.fitnesspark.app/fitnesspark/attendees'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://member.fr.fitnesspark.app/fitnesspark/',
        'Origin': 'https://member.fr.fitnesspark.app',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/75.0.3770.90 Chrome/75.0.3770.90 Safari/537.36',
        'Authorization': 'Bearer ' + session.access_token,
        'Content-Type': 'application/ld+json'
    }
    data = {
        'contactId': '/fitnesspark/contacts/398242',
        'contactClubId': '/fitnesspark/clubs/236',
        'contactNumber': '963139',
        'contactFamilyName': 'DANNA',
        'contactGivenName': 'ANNICK',
        'contactCreatedAt': '2014-09-03T00:00:00+02:00',
        'classEvent': '/fitnesspark/class_events/{0}'.format(theClazz.id)
    }
    resp: Response = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.status_code != requests.codes.ok:
        raise Exception("Can't fetch URL: {0} {1}".format(resp.status_code, resp.content))


session: Session = login(CUSTOMER_ACCOUNT_ID, CUSTOMER_ACCOUNT_PWD, CUSTOMER_CLIENT_ID, CUSTOMER_CLIENT_SECRET)

register(session, Activity.ZUMBA, datetime(2019, 6, 27, 19, 15, 0, 0, FRANCE_TZ))
