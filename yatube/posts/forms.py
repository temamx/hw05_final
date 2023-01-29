from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = {'text', 'group', 'image'}
        labels = {
            'text': _('Текст поста'),
            'group': _('Название группы')
        }
        help_text = {
            'text': _('Это просто текст поста'),
            'group': _('А это просто название группы')
        }


class CommentForm(forms.ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария'
        }
