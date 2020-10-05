from django import forms
from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("group", "text")
        widgets = {
            "text": forms.Textarea,
        }
        labels = {
            "group": "Группа",
            "text": "Текст",
        }
        help_texts = {
            "group": "Укажите сообщество, в котором хотите опубликовать пост.",
            "text": "Напишите текст поста.",
        }
