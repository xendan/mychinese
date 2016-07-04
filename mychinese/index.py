from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from lesson.models import PaidCounter


@login_required
def index(request):
    counter = PaidCounter.load()
    return  render_to_response('main.html', {'paid_num':counter.num}, context_instance=RequestContext(request))

