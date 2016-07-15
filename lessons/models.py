from django.db import models
from datetime import datetime 

class HomeWork(models.Model):
    task = models.TextField()
    answer = models.TextField()
    correct = models.TextField()

    def __str__(self):
        return self.task

class Dialog(models.Model):

    link = models.CharField(max_length = 250)
    name = models.TextField()
    lessons_in_dict = models.BooleanField(default=False)

    def __str__(self):
        return "Link=%s; in dict= %s" % (self.link, self.lessons_in_dict)

class Lesson(models.Model):
    date = models.DateTimeField(default=datetime.now)
    home_work =  models.OneToOneField(HomeWork, related_name = 'lesson', null=True, blank=True)
    dialog =  models.OneToOneField(Dialog, related_name = 'lesson', null=True, blank=True)

    def __str__(self):
        return self.date.__str__()

    class Meta:
        get_latest_by = 'date'

class Word(models.Model):
    chinese =  models.CharField(max_length = 10)
    pinyin = models.CharField(max_length = 10)
    translation = models.CharField(max_length = 250)
    lesson = models.ForeignKey(Lesson, related_name = 'lessons')

    def __str__(self):
        return "%s %s %s" % (self.chinese, self.pinyin, self.translation)

class Note(models.Model):
    content = models.TextField()
    store_in_grammar = models.BooleanField(default=False)
    image = models.ImageField()
    lesson = models.ForeignKey(Lesson, related_name = 'notes')
    def __str__(self):
        return self.content


class PaidCounter(models.Model):
    num = models.PositiveSmallIntegerField(default = 0)

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(PaidCounter, self).save(*args, **kwargs)

    def __str__(self):
        return self.num

    @classmethod
    def load(cls):
         try:
             return cls.objects.get()
         except cls.DoesNotExist:
             return cls()
