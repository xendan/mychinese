from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.conf  import settings
from django.contrib.auth import authenticate, login

@csrf_protect
def index(request):
    if not request.user.is_authenticated():
        return  render_to_response('login.html', {}, context_instance=RequestContext(request))
    elif request.method == 'POST':
         username = request.POST['login']
         password = request.POST['password']
         user = authenticate(username=username, password=password)
         if user is not None:
             if user.is_active:
                 login(request, user)
                 return  render_to_response('main.html', {}, context_instance=RequestContext(request))
             #else: TODO when is this?
                                                                                     # Return a 'disabled account' error message
                                                             # Redirect to a success page.
    #temp_vars = {'form' : form, 'categories':categories, 'page_size':settings.PAGE_SIZE}    
    else:
        return  render_to_response('main.html', {}, context_instance=RequestContext(request))
