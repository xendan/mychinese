from django.utils import six
import json

import sys
from django.core.serializers.json import Serializer as Builtin_Serializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect

from lessons.models import PaidCounter, Lesson, Dialog, HomeWork, Note, Word

from django.core.serializers.base import DeserializationError
from django.core.serializers.python import (
    Deserializer as PythonDeserializer, Serializer as PythonSerializer,
)

class MySerializer(Builtin_Serializer):
    def to_json(self, obj, **options):
        if obj:
            fields = options.pop("fields", None)
            try:
                (o for o in obj)
            except TypeError:
                return self.serialize([obj,], fields=fields)[1:-1]
            return self.serialize(obj, fields=fields)

    def get_dump_object(self, obj):
        data = super(MySerializer, self).get_dump_object(obj)
        data["fields"]["id"] = data["pk"]
        return data["fields"]

    def from_json(self, model, source, **options):
        """
        Deserialize a stream or string of JSON data.
        """
        def to_django_obj(obj):
            if "id" in obj:
                id = obj["id"]
                del obj["id"]
            else:
                id = -1

            return {"model":model, "pk":id, "fields": obj}
        need_load_json = False
        if isinstance(source, dict):
            objects = [source]
        elif isinstance(source, list):
            objects = source
        elif not isinstance(source, (bytes, six.string_types)):
            need_load_json = True
            source = source.read()
        if isinstance(source, bytes):
            need_load_json = True
            source = source.decode('utf-8')
        try:
            if need_load_json:
                objects = json.loads(source)
            django_objects = []
            for obj in objects:
                django_objects.append(to_django_obj(obj))
            for obj in PythonDeserializer(django_objects, **options):
                if obj.object.id == -1:
                    obj.object.id = None
                if isinstance(django_objects, list):
                    yield obj
        except GeneratorExit:
            raise
        except Exception as e:
            # Map to deserializer error
            six.reraise(DeserializationError, DeserializationError(e), sys.exc_info()[2])

my_serializer = MySerializer()

@csrf_protect
def pay_lessons(request):
    #TODO create nice rest
    if request.method == 'POST':
        lesson_num = request.POST.get('lesson_num')
        counter = PaidCounter.load()
        counter.num = int(lesson_num)
        counter.save()
        return JsonResponse({"lesson_num": lesson_num})
    else:
        return JsonResponse({"nothing to see": "this isn't happening"})

@csrf_protect
def create_lesson(request):
    def create_lesson_inst():
        dialog = Dialog()
        dialog.save()
        home_work = HomeWork()
        home_work.save()
        lesson = Lesson(dialog = dialog, home_work = home_work)
        lesson.save()
        return lesson

    counter = PaidCounter.load()
    #TODO: no lessons check
    counter.num -= 1
    counter.save()
    lesson_json = my_serializer.to_json(create_lesson_inst())
    return HttpResponse(lesson_json, content_type='application/json')

