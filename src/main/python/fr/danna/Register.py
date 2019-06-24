# import urllib
import json
import logging
import re
import string
import dateutil
from datetime import datetime
from enum import Enum
from typing import Pattern, Match

import pytz as pytz
import requests
from dataclasses import dataclass
from dateutil.parser import parse
from requests import Response

FRANCE_TZ = pytz.timezone('Europe/Paris')
# print(FRANCE_TZ._utcoffset)  # Prints '0:09:00' !?!

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class Customer:
    acccount_id: string
    accound_pwd: string
    client_id: string
    client_secret: string
    family_name: string
    given_name: string
    account_creation_date: string
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
    access_token: string
    expires_in: string
    refresh_token: string
    scope: string
    token_type: string


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
        resp_dict['token_type'],
    )
    return user_session


@dataclass
class Activity:
    identifier: int
    name: string


"""
Exhautive list of activities.
"""
ACTIVITY_ZUMBA = Activity(1547, 'Zumba')
ACTIVITY_CAF = Activity(1548, 'CAF')
ACTIVITY_TBC = Activity(1549, 'T.B.C.')
ACTIVITY_BIKING = Activity(1550, 'Biking')
ACTIVITY_CROSS_TRAINING = Activity(1551, 'Cross Training')
ACTIVITY_BODY_BARRE_ = Activity(1552, 'Body Barre')
ACTIVITY_HIIT = Activity(1553, 'HIIT')
ACTIVITY_BODY_SCULPT = Activity(1555, 'Body Sculpt')
ACTIVITY_PILATES = Activity(1556, 'Pilates')
ACTIVITY_CARDIO_ATTACK = Activity(1557, 'Cardio Attack')
ACTIVITY_INEXISTANT = Activity(1, 'INEXISTANT')


@dataclass
class ClassEvent:
    activity: Activity
    start_at: datetime
    id: int


CLASS_EVENT_ID_GROUP_NAME = 'id'
CLASS_EVENT_ID_PATTERN: Pattern = re.compile('^/fitnesspark/class_events/(?P<' + CLASS_EVENT_ID_GROUP_NAME + '>\\d+)$')


def check_event_start(class_event: ClassEvent, starting_at):
    """
    Check that the even given actually starts at the given date/time.
    :param class_event:
    :param starting_at:
    :return:
    """

    # NB: Timezones differ (why?). Must not consider them when comparing.
    # Cf. https://stackoverflow.com/questions/10944047/how-can-i-remove-a-pytz-timezone-from-a-datetime-object
    if class_event.start_at.replace(tzinfo=None) != starting_at.replace(tzinfo=None):
        raise Exception('Event does not start at the expected date/time: expecting {exp}, found {act}'
                        .format(exp=starting_at, act=class_event.start_at)
                        )


def class_event(session: Session, activity: Activity, starting_at: datetime) -> ClassEvent:
    url = 'https://api.fr.fitnesspark.app/fitnesspark/class_events'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://member.fr.fitnesspark.app/fitnesspark/',
        'Origin': 'https://member.fr.fitnesspark.app',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/75.0.3770.90 Chrome/75.0.3770.90 Safari/537.36',
        'Authorization': 'Bearer ' + session.access_token,
    }
    customer = session.customer
    club_id = customer.contact_club_id
    params = {
        'startedAt[after]': starting_at.strftime('%Y-%m-%d'),
        'order[startedAt]': 'asc',
        'activity': '/fitnesspark/activities/{0}'.format(activity.identifier),
        'club': '/fitnesspark/clubs/{0}'.format(club_id),
        'available': 'true',
    }
    resp: Response = requests.get(url, headers=headers, params=params)
    if resp.status_code != requests.codes.ok:
        raise Exception("Can't fetch URL: {0} {1}".format(resp.status_code, resp.content))
    resp_dict: dict = resp.json()
    class_events: dict = resp_dict['hydra:member']
    if len(class_events) == 0:
        raise Exception('No class event (available) for activity {act} starting at {start}.'
                        .format(act=activity.name, start=starting_at))
    first_class_event_dict: dict = class_events[0]
    class_event_id_tag: string = first_class_event_dict['@id']
    m: Match = CLASS_EVENT_ID_PATTERN.match(class_event_id_tag)
    if m is None:
        raise Exception("Can't find class event ID in '" + class_event_id_tag + "'.")
    class_event_id_tag: string = m.group(CLASS_EVENT_ID_GROUP_NAME)
    class_event_id: int = int(class_event_id_tag)
    start_str = first_class_event_dict.get('startedAt')
    start_dt: datetime = parse(start_str)
    class_evt = ClassEvent(activity, start_dt, class_event_id)

    check_event_start(class_evt, starting_at)

    return class_evt


def try_to_register(session: Session, activity: Activity, starting_at: datetime) -> bool:
    """
    Register the user of the given session to the given activity, at the given date.
    """

    try:
        class_evt: ClassEvent = class_event(session, activity, starting_at)
    except Exception as e:
        LOGGER.error(e)
        return False

    customer = session.customer
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
        'classEvent': '/fitnesspark/class_events/{0}'.format(class_evt.id)
    }
    resp: Response = requests.post(url, headers=headers, data=json.dumps(data))
    if resp.status_code != requests.codes.created:
        LOGGER.error("Can't fetch URL: {0} {1}".format(resp.status_code, resp.content))
        return False

    LOGGER.debug('Registered for activity {act} on {when}.'
                 .format(act=activity.name, when=starting_at.strftime('%d/%m/%Y at %H:%M')))
    return True


session: Session = login(CUSTOMER)

registration_success = 0
for (activity, start_at) in [
    (ACTIVITY_ZUMBA, datetime(2019, 6, 25, 12, 30, 0, 0, FRANCE_TZ)),
    (ACTIVITY_ZUMBA, datetime(2019, 6, 27, 19, 15, 0, 0, FRANCE_TZ))
]:
    registration_success += 1 if try_to_register(session, activity, start_at) else 0

LOGGER.info('Registration trial complete. {success} registration(s) have been successfully made.'
            .format(success=registration_success))
