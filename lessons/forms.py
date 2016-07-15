from django.forms import ModelForm

from lessons.models import Note


class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ["content", "store_in_grammar", "image"]