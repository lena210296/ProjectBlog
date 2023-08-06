from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Post, UserProfile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PostForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Post.STATUS_CHOICES)

    class Meta:
        model = Post
        fields = ['title', 'short_description', 'image', 'full_description', 'status']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'is_anonymous']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your Name')
    email = forms.EmailField(label='Your Email')
    subject = forms.CharField(widget=forms.Textarea, label='Subject')
    message = forms.CharField(widget=forms.Textarea, label='Your Message')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ContactForm, self).__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['name'].initial = user.username
