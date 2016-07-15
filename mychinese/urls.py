"""mychinese URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import re
from django.conf.urls import patterns,  url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.core import serializers
from django.http import HttpResponse, JsonResponse

from lessons.views import  pay_lessons, create_lesson, my_serializer
from lessons.models import Dialog, HomeWork, Note, Word
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#import logging
#logger = logging.getLogger(__name__)

admin.autodiscover()

rest_root = r'lessons/'

def class_to_url(cls):
    return re.escape(cls.__name__.lower())

def create_get(cls):
    def handler(request, obj_id):
        try:
            obj_json = my_serializer.to_json(cls.objects.get(pk = obj_id))
        except cls.DoesNotExist:
            obj_json = None
        return HttpResponse(obj_json, content_type="application/json")

    return url(rest_root + class_to_url(cls) + r'/([0-9]+)', handler)

def create_put(cls):
    def handler(request):
        if request.method == 'PUT':
            body_unicode = request.body.decode('utf-8')
            for obj in serializers.deserialize("json", "[" + body_unicode + "]"):
                obj.save()
            return HttpResponse(request.body, content_type="application/json")
        else:
            return JsonResponse({"nothing to see": "this isn't happening"})
    return url(rest_root + class_to_url(cls), handler)

def create_search(cls, param_name):
    def handler(request):
        try:
            param_value = request.GET.get(param_name, '')
            obj_json = serializers.serialize('json', cls.objects.filter(**{param_name : param_value}))
        except cls.DoesNotExist:
            obj_json = None
        return HttpResponse(obj_json, content_type="application/json")
    return url(rest_root + class_to_url(cls) + r'$', handler)

urlpatterns = [ create_get(HomeWork),
                create_get(Dialog),
                create_put(Dialog),
                create_search(Note, "lesson"),
                create_search(Word, "lesson"),
                 url(r'^$', 'mychinese.index.index'),
                 url(r'^pay_lessons', pay_lessons),
                 url(r'^lessons/lesson', create_lesson),

                  # Uncomment the admin/doc line below to enable admin documentation:
                  url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                  # Uncomment the next line to enable the admin:
                  url(r'^admin/', admin.site.urls),
                  url(r'^accounts/login/$', auth_views.login),
                  url(
                      regex=r'^login/$', 
                      view=login, 
                      kwargs={'template_name': 'login.html'}, 
                      name='login'
                   ),
                   url(
                      regex=r'^logout/$', 
                      view=logout, 
                      kwargs={'next_page': '/'}, 
                      name='logout'
                     ),
] 

urlpatterns += staticfiles_urlpatterns()