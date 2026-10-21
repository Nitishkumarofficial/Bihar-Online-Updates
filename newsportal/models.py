
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class NewsUpdate(models.Model):
    CATEGORY_CHOICES = [
        ('job', 'Latest Jobs'),
        ('result', 'Results'),
        ('admit_card', 'Admit Cards'),
        ('scholarship', 'Scholarships'),
        ('scheme', 'Government Schemes'),
        ('admission', 'Admissions'),
        ('other', 'Other Updates'),
    ]

    title = models.CharField(max_length=250)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    short_description = models.TextField()
    full_description = models.TextField(blank=True)
    organization = models.CharField(max_length=250, blank=True)
    total_vacancies = models.CharField(max_length=100, blank=True)
    eligibility = models.TextField(blank=True)
    age_limit = models.TextField(blank=True)
    application_fee = models.TextField(blank=True)
    important_dates = models.TextField(blank=True)
    selection_process = models.TextField(blank=True)
    published_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_date = models.DateField(null=True, blank=True)
    official_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'update-detail',
            kwargs={'pk': self.pk, 'slug': slugify(self.title) or 'update'},
        )
