from django.forms import ModelForm
from ninja_apikey.models import APIKey


class APIKeyForm(ModelForm):
    class Meta:
        model = APIKey
        fields = ["label"]
