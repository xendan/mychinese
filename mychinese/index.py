from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from lessons.models import PaidCounter, Lesson
from lessons.views import my_serializer


@login_required
def index(request):
    counter = PaidCounter.load()
    try:
        lesson_json = my_serializer.to_json(Lesson.objects.last())
    except Lesson.DoesNotExist:
        lesson_json = None
    return  render_to_response('main.html', {'paid_num':counter.num, 'lesson': lesson_json}, context_instance=RequestContext(request))

