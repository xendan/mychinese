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
import logging
logger = logging.getLogger(__name__)

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

def create_put_post_search(cls, param_name):
    def handler(request):
        if request.method == 'PUT' or request.method == 'POST':
            obj_str_json = request.body.decode('utf-8')
            id_re = r"pk\s+=\s(.+)"
            regexp = re.compile(id_re)
            is_new = False
            null_id="\"pk\":\"-1\","
            if regexp.search(obj_str_json) is None:
                is_new = True
                obj_str_json = "{" + null_id + obj_str_json.strip()[1:]
            #django don't deserialize without id
            for obj in serializers.deserialize("json", "[" + obj_str_json + "]"):
                if is_new:
                    obj.object.pk = None 
                    obj.object.id = None 
                new_id = obj.save()
                if is_new:
                    obj_str_json.replace(null_id, "\"pk\":\"%d\"," % new_id)
            return HttpResponse(new_id, content_type="application/json")
        elif request.method == 'GET':
            try:
                param_value = request.GET.get(param_name, '')
                obj_json = serializers.serialize('json', cls.objects.filter(**{param_name : param_value}))
            except cls.DoesNotExist:
                obj_json = None
            return HttpResponse(obj_json, content_type="application/json")
        else:
            return JsonResponse({"error": "PUT and POST are supported"})
    return url(rest_root + class_to_url(cls), handler)

urlpatterns = [ create_get(HomeWork),
                create_get(Dialog),
                create_put_post_search(Dialog, "lesson"),
                create_put_post_search(Note, "lesson"),
                create_put_post_search(Word, "lesson"),
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
