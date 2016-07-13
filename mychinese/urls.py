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
from django.conf.urls import patterns,  url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login
from django.contrib.auth.views import logout
from django.http import HttpResponse, JsonResponse

from lessons.views import  pay_lessons, create_lesson, my_serializer
from lessons.models import Dialog, HomeWork


admin.autodiscover()


def create_get(cls):
    def handler(request, obj_id):
        try:
            obj_json = my_serializer.to_json(cls.objects.get(pk = obj_id))
        except cls.DoesNotExist:
            obj_json = None
        return JsonResonse(obj_json) 

    return url(r'^lessons/%s/([0-9]+)', handler)

urlpatterns = [ create_get(HomeWork),
                create_get(Dialog),
                 url(r'^$', 'mychinese.index.index'),
                 url(r'^pay_lessons', pay_lessons),
                 url(r'^lesson', create_lesson),

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
