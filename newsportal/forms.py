from django import forms

from .models import NewsUpdate


class UpdateSearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=250, strip=True)
    category = forms.ChoiceField(
        required=False,
        choices=(('', 'All categories'), *NewsUpdate.CATEGORY_CHOICES),
    )
    published_after = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    published_before = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        published_after = cleaned_data.get('published_after')
        published_before = cleaned_data.get('published_before')
        if published_after and published_before and published_after > published_before:
            self.add_error(
                'published_before',
                'End date must be on or after the start date.',
            )
        return cleaned_data
