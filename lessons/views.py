from django.core.serializers.json import Serializer as Builtin_Serializer
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect

from lessons.models import PaidCounter, Lesson, Dialog, HomeWork, Note, Word


class MySerializer(Builtin_Serializer):
    def to_json(self, obj, **options):
        if obj:
            fields = options.pop("fields", None)
            return self.serialize([obj,], fields=fields)[1:-1]

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
    counter.num = counter.num - 1
    counter.save()
    lesson_json = my_serializer.to_json(create_lesson_inst())
    return HttpResponse(lesson_json, content_type='application/json')

