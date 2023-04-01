from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Post, Profile, Comment, CommentReply
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django.contrib import messages
import django_filters
import re
from urllib.parse import urlparse
import html
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
import sys
from PIL import Image


def sanitize_input(url):
    # Check if the input contains JavaScript code
    if re.search(r'<script.*?>.*?</script>', url, re.DOTALL | re.IGNORECASE):
        # Escape the input to protect against XSS attacks
        url = html.escape(url)
    return url


def url_validator(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(regex, url) is not None:
        parsed_url = urlparse(url)
        if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc:
            sanitized_url = sanitize_input(url)
            return True
    return False


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='Gorl Name')
    email = forms.EmailField(label='GorlMail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('password1', css_class='form-control'),
            Field('password2', css_class='form-control'),
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Sorry Gorl, please choose another email.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Sorry Gorl, please choose another username.")
        return username

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):

    username = forms.CharField(label='Gorl Name', max_length=254)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': ("Please enter a correct %(username)s and password Gorl. "
                          "Note that both fields may be case-sensitive Haydur."),
        'inactive': ("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.error_css_class = 'hot-pink-banner'
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password', css_class='form-control'),
        )

    def add_error(self, message, field=None):
        # Do not add any errors to the form
        pass


class PostForm(forms.ModelForm):
    files = forms.FileField(required=False)
    file_url = forms.URLField(required=False)
    delete_files = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Field('title', css_class='form-control'),
            Field('body', css_class='form-control'),
            Field('files', css_class='form-control'),
            Field('file_url', css_class='form-control'),
            Field('delete_files', css_class='form-control'),
        )

    def clean(self):
        cleaned_data = super().clean()
        files = cleaned_data.get("files")
        file_url = cleaned_data.get("file_url")
        max_size = 2 * 1024 * 1024  # 2MB
        if files and file_url:
            self.add_error("files", "Can only post a file or a URL, not both.")
            self.add_error(
                "file_url", "Can only post a file or a URL, not both..")
        if files and files.size > max_size:
            self.add_error("files", "File size should not exceed 2MB.")
        if file_url and not url_validator(file_url):
            self.add_error("file_url", "Please enter a valid URL.")

    def clean_files(self):
        files = self.cleaned_data.get("files")
        max_size = 2 * 1024 * 1024  # 2MB

        if files:
            if not hasattr(files, 'content_type'):
                return files
            if files.size > max_size:
                self.add_error("files", "File size should not exceed 2MB.")
            else:
                if files.content_type != "image/gif":
                    img = Image.open(files)
                    width, height = img.size

                    if width > height:
                        factor = width / 500
                        img = img.resize(
                            (500, int(height / factor)), Image.ANTIALIAS)
                    else:
                        factor = height / 500
                        img = img.resize(
                            (int(width / factor), 500), Image.ANTIALIAS)

                    supported_formats = ['jpeg', 'JPEG',
                                         'png', 'PNG', 'gif', 'GIF']
                    file_extension = files.name.split('.')[-1].upper()
                    if file_extension not in supported_formats:
                        self.add_error("files", "Unsupported file format.")

                    output = io.BytesIO()
                    img.save(output, format=file_extension)
                    output.seek(0)
                    files = InMemoryUploadedFile(
                        output, 'ImageField', files.name, files.content_type, sys.getsizeof(output), None)
                return files

    class Meta:
        model = Post
        fields = ['title', 'body', 'files', 'file_url', 'delete_files']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 10, 'cols': 30}),
        }


class UpdateProfileForm(forms.ModelForm):
    username = forms.CharField(label='Gorl Name')
    email = forms.EmailField(label='GorlMail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
        )

    class Meta:
        model = User
        fields = ['username', 'email', ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            self.add_error('email', "Sorry Gorl, email already taken.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")
        current_image = self.instance.image
        if image and (not current_image or current_image.name != image.name):
            if current_image and self.instance.image.name != 'default.png':
                current_image.delete(save=False)
            self.instance.image = image
            self.cleaned_data['image'] = image
        return cleaned_data


class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    username = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Post
        fields = ['title', 'username']


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ["content"]


class CommentReplyForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CommentReply
        fields = ["content"]
