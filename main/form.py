from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserRegistrationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget = forms.widgets.TextInput({'class': 'form-control'})
        self.fields['password'].widget = forms.widgets.PasswordInput({'class': 'form-control'})