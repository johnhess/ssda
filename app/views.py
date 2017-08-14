import datetime
import os

from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext

import redis


REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost')


def get_db():
    return redis.StrictRedis.from_url(REDIS_URL)

def store_message(message):
    get_db().set(datetime.datetime.utcnow(), message.encode('utf-8'))

def get_messages():
    """All messages in reverse chronological order."""
    db = get_db()
    return [
        db.get(key).decode('utf-8') 
        for key in reversed(sorted(db.keys()))
    ]

def home(request):
    return render(request=request, template_name='templates/home.html')

def guestbook(request):
    # version 2.0
    # CSRF Middleware protects this by default in Django

    # store the new message, if there is one
    if request.method == 'POST':
        store_message(request.POST.get('message'))
    # either way, give back the list of messages
    context = {'messages': get_messages()}
    return render(
        request=request,
        template_name='templates/guestbook.html',
        context=context
    )

def greeter(request):
    # Not used in the talk, but here's a vulnerable django greeter
    who = request.GET.get('name', 'friend')
    return HttpResponse("Hello, {}".format(who))

def nuke(request):
    """Clears the guestbook message board."""
    get_db().flushall()
    return HttpResponse('database nuked')
