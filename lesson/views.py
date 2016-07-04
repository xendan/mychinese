import json

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_protect

from lesson.models import PaidCounter

@csrf_protect
def pay_lessons(request):
    if request.method == 'POST':
        lesson_num = request.POST.get('lesson_num')
        counter = PaidCounter.load()
        counter.num = int(lesson_num)
        counter.save()
        return HttpResponse(json.dumps({"lesson_num": lesson_num}))
    else:
        return HttpResponse(json.dumps({"nothing to see": "this isn't happening"}),
                                  content_type="application/json")

