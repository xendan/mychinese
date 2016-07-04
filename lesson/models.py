from django.db import models

class HomeWork(models.Model):
    task = models.TextField()
    answer = models.TextField()
    correct = models.TextField()

class Lesson(models.Model):
    date = models.DateTimeField()
    home_work =  models.OneToOneField(HomeWork, related_name = 'lesson')

class Word(models.Model):
    chinese =  models.CharField(max_length = 10)
    pinyin = models.CharField(max_length = 10)
    translation = models.CharField(max_length = 250)
    lesson = models.ForeignKey(Lesson, related_name = 'words')

class Note(models.Model):
    content = models.TextField()
    store_in_grammar = models.BooleanField(default=False)
    image = models.ImageField()
    lesson = models.ForeignKey(Lesson, related_name = 'notes')

class Dialog(models.Model):
    link = models.CharField(max_length = 250)
    words_in_dict = models.BooleanField(default=False)
    lesson = models.ForeignKey(Lesson, related_name='dialogs')
    def __str__(self):
        return "Link=%s; in dict= %s" % (self.link, self.words_in_dict)

class PaidCounter(models.Model):
    num = models.PositiveSmallIntegerField(default = 0)

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(PaidCounter, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
         try:
             return cls.objects.get()
         except cls.DoesNotExist:
             return cls()
