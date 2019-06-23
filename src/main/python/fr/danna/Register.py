# import urllib
import json
from datetime import datetime
from enum import Enum

import pytz as pytz
import requests
from dataclasses import dataclass
from requests import Response

FRANCE_TZ = pytz.timezone('Europe/Paris')


@dataclass
class Customer:
    acccount_id: str
    accound_pwd: str
    client_id: str
    client_secret: str
    family_name: str
    given_name: str
    account_creation_date: str
    contact_id: int
    contact_number: int
    contact_club_id: int


CUSTOMER = Customer(
    'annick.danna@gmail.com',
    'Resamania2019',
    '4_5pq41l35lao848k44kk84ssc8kgkcswo0s0k040cwkgw4ko8g4',
    '1qnd586ifbesc4444cc0o8g4sw4g4kwcco0owg8o4ccg48ssog',
    'DANNA',
    'ANNICK',
    '2014-09-03T00:00:00+02:00',
    398242,
    963139,
    236
)


@dataclass
class Session:
    customer: Customer
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str


def login(customer: Customer) -> Session:
    """
    Logs in (authent) the given user.
    :param customer:
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
        'username': customer.acccount_id,
        'password': customer.accound_pwd,
        'client_id': customer.client_id,
        'client_secret': customer.client_secret,
        'redirect_uri': 'https://member.fr.fitnesspark.app/fitnesspark/',
    }
    resp: Response = requests.post(url, headers=headers, data=data)
    if resp.status_code != requests.codes.ok:
        raise Exception("Can't fetch URL: {0} {1}".format(resp.status_code, resp.content))
    resp_dict = resp.json()
    user_session = Session(
        customer,
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

    customer = session.customer

    class_event: Class = clazz(activity, when)

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
        'contactId': '/fitnesspark/contacts/{0}'.format(customer.contact_id),
        'contactClubId': '/fitnesspark/clubs/{0}'.format(customer.contact_club_id),
        'contactNumber': '{0}'.format(customer.contact_number),
        'contactFamilyName': customer.family_name,
        'contactGivenName': customer.given_name,
        'contactCreatedAt': customer.account_creation_date,
        'classEvent': '/fitnesspark/class_events/{0}'.format(class_event.id)
    }
    resp: Response = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.status_code != requests.codes.created:
        raise Exception("Can't fetch URL: {0} {1}".format(resp.status_code, resp.content))


session: Session = login(CUSTOMER)

register(session, Activity.ZUMBA, datetime(2019, 6, 27, 19, 15, 0, 0, FRANCE_TZ))
