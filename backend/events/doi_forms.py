"""Input and review forms; identity never comes from submitted hidden fields."""

from django import forms
from django.core.validators import URLValidator

from .models import Resource
from .services.doi import normalize_doi


class DoiLookupForm(forms.Form):
    doi = forms.CharField(label="DOI or DOI link", strip=False, max_length=8192)

    def clean_doi(self):
        normalize_doi(self.cleaned_data["doi"])
        return self.cleaned_data["doi"]


class DoiReviewForm(forms.Form):
    title = forms.CharField(max_length=500)
    authors = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    year = forms.IntegerField(required=False, min_value=1, max_value=9999)
    original_url = forms.URLField(
        label="Original URL", max_length=2048,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    resource_type = forms.ChoiceField(choices=Resource.ResourceType.choices)
    recommendation = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    display_order = forms.IntegerField(initial=0, min_value=-2147483648, max_value=2147483647)

    def __init__(self, *args, bibliography, existing=False, **kwargs):
        super().__init__(*args, initial={**bibliography, "display_order": 0}, **kwargs)
        if existing:
            # Disabled fields use trusted initial values even for forged POSTs.
            for field in bibliography:
                self.fields[field].disabled = True
                if isinstance(self.fields[field], forms.CharField):
                    self.fields[field].strip = False
