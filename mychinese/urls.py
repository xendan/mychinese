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
import json
from django.conf.urls import patterns,  url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.http import HttpResponse, JsonResponse

from lessons.forms import NoteForm
from lessons.views import  pay_lessons, create_lesson, my_serializer
from lessons.models import Dialog, HomeWork, Note, Word
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import QueryDict

import logging
logger = logging.getLogger("django")

admin.autodiscover()

#TODO move to lessons
module_name = "lessons"
rest_root = re.escape(module_name) + r'/'


def class_to_url(cls):
    def camel_case_to_snake(name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return re.escape(camel_case_to_snake(cls.__name__))


def bad_request(message):
    return JsonResponse({"error": message}, status=400)


def create_get_and_delete(cls):
    def handler(request, obj_id):
        if request.method == 'GET':
            try:
                obj_json = my_serializer.to_json(cls.objects.get(pk=obj_id))
            except cls.DoesNotExist:
                obj_json = {}
            return HttpResponse(obj_json, content_type="application/json")
        if request.method == 'DELETE':
            cls.objects.filter(id=obj_id).delete()
            return JsonResponse({})
        else:
            return bad_request("DELETE and GET are supported")

    return url(rest_root + class_to_url(cls) + r'/([0-9]+)$', handler)


def create_put_post_search(cls, param_name, form_cls=None):
    def handler(request):
        def to_model_name():
            return module_name + "." + cls.__name__.lower()

        if request.method == 'GET':
            try:
                param_value = request.GET.get(param_name, '')
                obj_dict = my_serializer.to_json(cls.objects.filter(**{param_name: param_value}))
                if obj_dict is None:
                    obj_dict = [[]]
            except cls.DoesNotExist:
                obj_dict = []
            return HttpResponse(obj_dict, content_type="application/json")

        if request.method == 'PUT' or request.method == 'POST':
            if form_cls is None:
                obj_dict = json.loads(request.body.decode('utf-8'))
                for obj in my_serializer.from_json(to_model_name(), obj_dict):
                    obj.save()
                    obj_dict["id"] = obj.object.id
            else:
                if request.method == "PUT":
                    #TODO return 404
                    req_param = QueryDict(request.body)
                    obj_inst = cls.objects.get(pk=req_param.get("id"))
                    form = form_cls(QueryDict(request.body), instance=obj_inst)
                else:
                    obj_inst = cls()
                    form = form_cls(request.POST, instance=obj_inst)

                if form.is_valid():
                    form.save()
                    obj_dict = my_serializer.to_json(obj_inst)
                else:
                    obj_dict = json.dumps(form.errors)
            return HttpResponse(obj_dict, content_type="application/json")
        else:
            return bad_request("PUT, POST and GET are supported")

    return url(rest_root + class_to_url(cls) + r'$', handler)


urlpatterns = [create_get_and_delete(HomeWork),
               create_put_post_search(HomeWork, "lesson"),
               create_get_and_delete(Dialog),
               create_get_and_delete(Word),
               create_get_and_delete(Note),
               create_put_post_search(Dialog, "lesson"),
               create_put_post_search(Word, "lesson"),
               create_put_post_search(Note, "lesson", NoteForm),
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
