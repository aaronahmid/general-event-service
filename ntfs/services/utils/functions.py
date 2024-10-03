"""
"""

# imports
import datetime
import requests
from config.settings import getvar
from typing import Union, List, Dict


def now_with_timezone():
    # Define the timezone offset (+01:00)
    offset = datetime.timedelta(hours=1)
    tz = datetime.timezone(offset)

    # Get the current date and time with the specified timezone
    now_with_timezone = datetime.datetime.now(tz)

    # Format the date and time in the specified format
    formatted_now_with_timezone = now_with_timezone.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    # Ensure the microseconds part is correctly formatted (6 digits)
    formatted_now_with_timezone = (
        formatted_now_with_timezone[:-2] + ":" + formatted_now_with_timezone[-2:]
    )

    return formatted_now_with_timezone


def generate_timestamp():
    now = datetime.datetime.now()
    return now.timestamp


def generate_30min_timestamp():
    # Get the current time
    current_time = datetime.datetime.now()

    # Add 30 minutes to the current time
    time_30_minutes_from_now = current_time + datetime.timedelta(minutes=30)

    # Convert the result to a timestamp (Unix timestamp, which is the number of seconds since January 1, 1970)
    timestamp = int(time_30_minutes_from_now.timestamp())

    return timestamp


def format_response_data(data: Union[List, Dict], status: int, message="success!"):
    return {"message": "success!", "status_code": status, "payload": data}


def round_to_nearest_multiple(value, multiple):
    return round(value, multiple)


def lbs_to_kg(lbs):
    return lbs / 2.2046


def kg_to_lbs(kg):
    return kg * 2.2046


def convert_datetime_string(datetime_string):
    return str(datetime_string.replace(" ", "T")) + "GMT+01:00"


def five_days_from_now():  # sourcery skip: inline-immediately-returned-variable
    # Get the current datetime
    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=5)
    rounded = future.replace(microsecond=0, second=future.second)
    datetime_string = str(rounded)
    formatted_string = convert_datetime_string(datetime_string)

    return formatted_string


def one_day_from_now():  # sourcery skip: inline-immediately-returned-variable
    # Get the current datetime
    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=1)
    rounded = future.replace(microsecond=0, second=future.second)
    datetime_string = str(rounded)
    formatted_string = convert_datetime_string(datetime_string)

    return formatted_string


def today():  # sourcery skip: inline-immediately-returned-variable
    # Get the current date
    current_date = datetime.date.today()
    # Convert the date to a string in the desired format
    current_date_string = current_date.strftime("%Y-%m-%d")
    # Return the date string
    return current_date_string


def today_string():
    initial_date = str(today())
    date_list = initial_date.split("-")
    return "".join(date_list)


def flatten_list(data):
    flattened_list = []
    for sublist in data:
        flattened_list.extend(iter(sublist))
    return flattened_list
