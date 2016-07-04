from django.contrib import admin
from lesson.models import Lesson, Word, Note, Dialog, PaidCounter

admin.site.register(Lesson)
admin.site.register(Word)
admin.site.register(Note)
admin.site.register(Dialog)
admin.site.register(PaidCounter)
# Register your models here.
