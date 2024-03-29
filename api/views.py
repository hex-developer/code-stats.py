import datetime
import json

from django.http.response import (HttpResponse, HttpResponseBadRequest,
                                  HttpResponseNotAllowed, JsonResponse)
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Machine, XPEntry

# Create your views here.


@csrf_exempt
def pulses(request):
    data = json.loads(request.body.decode())
    if len(Machine.objects.all().filter(token=request.headers["X-Api-Token"])) > 0:
        for i in data['xps']:
            obj = XPEntry()
            obj.language = i['language']
            obj.xp = i['xp']
            obj.date = data['coded_at']
            obj.date = check_date(obj.date)
            if not obj.date:
                return HttpResponseBadRequest()
            obj.machine = Machine.objects.all().filter(
                token=request.headers["X-Api-Token"])[0].name
            obj.user = Machine.objects.all().filter(
                token=request.headers["X-Api-Token"])[0].user
            obj.save()
    else:
        return HttpResponseNotAllowed()
    # print(data)
    return JsonResponse(data={"ok": "Great success!"}, status=201)


def users(request, name):
    total_xp = get_total_xp(name)
    new_xp = get_new_xp(name)
    machines = {}
    languages = {}
    dates = {}
    for machine in Machine.objects.all().filter(user=name):
        machines[machine.name] = {"xps": get_machine_total_xp(
            name, machine.name), "new_xps": get_machine_new_xp(name, machine.name)}
        print(get_machine_new_xp(name, machine.name))
    for language in get_languages(name):
        languages[language] = {"xps": get_language_total_xp(
            name, language), "new_xps": get_language_new_xp(name, language)}
    for date in XPEntry.objects.all().filter(user=name):
        if not get_date(date.date) in dates:
            dates[get_date(date.date)] = date.xp
        else:
            dates[get_date(date.date)] += date.xp
    return JsonResponse({"user": name, "total_xp": total_xp, "new_xp": new_xp, "machines": machines, "languages": languages, "dates": dates})


def get_total_xp(user):
    total_xp = 0
    for entry in XPEntry.objects.all().filter(user=user):
        total_xp += entry.xp
    return total_xp


def get_new_xp(user):
    new_xp = 0
    for entry in XPEntry.objects.all().filter(date__gt=(datetime.datetime.now() - datetime.timedelta(hours=12)), user=user):
        new_xp += entry.xp
    return new_xp


def get_machine_total_xp(user, machine):
    total_xp = 0
    for entry in XPEntry.objects.all().filter(user=user, machine=machine):
        total_xp += entry.xp
    return total_xp


def get_machine_new_xp(user, machine):
    new_xp = 0
    for entry in XPEntry.objects.all().filter(date__gt=(datetime.datetime.now() - datetime.timedelta(hours=12)), user=user, machine=machine):
        new_xp += entry.xp
    return new_xp


def get_languages(user):
    languages = []
    for entry in XPEntry.objects.all().filter(user=user):
        if not entry.language in languages:
            languages.append(entry.language)
    return languages


def get_language_total_xp(user, language):
    total_xp = 0
    for entry in XPEntry.objects.all().filter(user=user, language=language):
        total_xp += entry.xp
    return total_xp


def get_language_new_xp(user, language):
    new_xp = 0
    for entry in XPEntry.objects.all().filter(date__gt=(datetime.datetime.now() - datetime.timedelta(hours=12)), user=user, language=language):
        new_xp += entry.xp
    return new_xp


def check_date(timestamp):
    # Convert the timestamp string to a datetime object
    timestamp_datetime = datetime.datetime.fromisoformat(timestamp)

    # Get the current datetime
    current_datetime = timezone.now()

    # Calculate the difference between the current datetime and the timestamp
    difference = current_datetime - timestamp_datetime

    # Check if the difference is greater than a week (7 days)
    if difference > datetime.timedelta(days=7):
        return False
    else:
        if timestamp_datetime > current_datetime:
            return current_datetime
        else:
            return timestamp_datetime


def get_date(timestamp):
    # Convert the timestamp string to a datetime object
    timestamp_datetime = datetime.datetime.fromisoformat(str(timestamp))

    # Extract the date part from the datetime object
    date = timestamp_datetime.date()

    # Convert the date object to a string in the desired format
    date_string = date.strftime("%Y-%m-%d")

    return date_string
