from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import render
from django.urls import path, reverse

from .models import NewsUpdate


class DashboardAdminSite(admin.AdminSite):
    site_header = 'Bihar Online Updates CMS'
    site_title = 'Bihar Online Updates Admin'
    index_title = 'Content dashboard'
    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        context = dict(extra_context or {})
        update_admin = self._registry.get(NewsUpdate)
        can_view_updates = bool(
            update_admin and update_admin.has_view_permission(request)
        )
        can_add_updates = bool(
            update_admin and update_admin.has_add_permission(request)
        )
        context['dashboard_can_view_updates'] = can_view_updates
        context['dashboard_can_add_updates'] = can_add_updates
        context['dashboard_stats'] = {}
        context['dashboard_recent_updates'] = []
        context['dashboard_navigation'] = [
            {
                'title': 'Dashboard',
                'links': [
                    {'label': 'Overview', 'url': reverse('admin:index')},
                ],
            },
        ]

        if can_view_updates:
            counts = NewsUpdate.objects.aggregate(
                total=Count('pk'),
                jobs=Count('pk', filter=Q(category='job')),
                scholarships=Count('pk', filter=Q(category='scholarship')),
                schemes=Count('pk', filter=Q(category='scheme')),
                results=Count('pk', filter=Q(category='result')),
                admissions=Count('pk', filter=Q(category='admission')),
                drafts=Count('pk', filter=Q(is_active=False)),
                published=Count('pk', filter=Q(is_active=True)),
            )
            context['dashboard_stats'] = counts
            context['dashboard_recent_updates'] = NewsUpdate.objects.order_by(
                '-updated_at',
                '-published_date',
                '-pk',
            )[:5]

        content_links = []
        if can_view_updates:
            change_list_url = reverse(
                'admin:newsportal_newsupdate_changelist'
            )
            content_links.append(
                {'label': 'All Updates', 'url': change_list_url}
            )
            for value, label in NewsUpdate.CATEGORY_CHOICES:
                content_links.append(
                    {
                        'label': label,
                        'url': f'{change_list_url}?category__exact={value}',
                    }
                )
        if can_add_updates:
            add_url = reverse('admin:newsportal_newsupdate_add')
            if not can_view_updates:
                content_links.append(
                    {'label': 'Add an Update', 'url': add_url}
                )

        if content_links:
            context['dashboard_navigation'].append(
                {
                    'title': 'Content Management',
                    'links': content_links,
                }
            )

        website_links = [
            {'label': 'View Public Website', 'url': reverse('home')},
            {
                'label': 'View All Public Updates',
                'url': reverse('legacy-all-updates'),
            },
        ]
        context['dashboard_navigation'].append(
            {'title': 'Website', 'links': website_links}
        )

        system_links = []
        user_admin = self._registry.get(get_user_model())
        if user_admin and user_admin.has_view_permission(request):
            system_links.append(
                {
                    'label': 'Users',
                    'url': reverse('admin:auth_user_changelist'),
                }
            )
        group_admin = self._registry.get(Group)
        if group_admin and group_admin.has_view_permission(request):
            system_links.append(
                {
                    'label': 'Groups',
                    'url': reverse('admin:auth_group_changelist'),
                }
            )
        if system_links:
            context['dashboard_navigation'].append(
                {'title': 'System', 'links': system_links}
            )

        return super().index(request, context)


admin_site = DashboardAdminSite(name='admin')
admin_site.register(get_user_model(), UserAdmin)
admin_site.register(Group, GroupAdmin)


class NewsUpdateForm(forms.ModelForm):
    class Meta:
        model = NewsUpdate
        fields = '__all__'
        widgets = {
            'last_date': forms.DateInput(attrs={'type': 'date'}),
            'important_dates': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.Textarea(attrs={'rows': 8}),
            'eligibility': forms.Textarea(attrs={'rows': 4}),
            'age_limit': forms.Textarea(attrs={'rows': 3}),
            'application_fee': forms.Textarea(attrs={'rows': 3}),
            'selection_process': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'title': 'Use the official update title shown to visitors.',
            'category': (
                'Controls the category label and the category filter '
                'used on the public updates list.'
            ),
            'short_description': (
                'A concise summary displayed on homepage and updates-list '
                'cards.'
            ),
            'full_description': (
                'Shown on this update’s detail page. If left blank, the '
                'short description is used instead.'
            ),
            'organization': (
                'Department, institution, exam board, or scheme provider '
                'named in the official notice.'
            ),
            'total_vacancies': (
                'For job updates, enter the number or wording from the '
                'official notice.'
            ),
            'eligibility': (
                'Enter verified qualifications or eligibility requirements; '
                'leave blank if not applicable.'
            ),
            'age_limit': (
                'Enter the age criteria from the official notice, if any.'
            ),
            'application_fee': (
                'Enter the fee details from the official notice, if any.'
            ),
            'important_dates': (
                'List other relevant dates as readable text, one date or '
                'milestone per line.'
            ),
            'selection_process': (
                'Describe the selection steps when the official notice '
                'provides them.'
            ),
            'last_date': (
                'Optional closing date. Leave empty when there is no '
                'confirmed deadline.'
            ),
            'official_link': (
                'Optional direct URL to the official notice, result, or '
                'application page.'
            ),
            'is_active': (
                'Checked updates are visible publicly. Unchecked updates '
                'are drafts and are hidden from public pages.'
            ),
        }
        labels = {
            'is_active': 'Published on the public website',
        }


@admin.register(NewsUpdate, site=admin_site)
class NewsUpdateAdmin(admin.ModelAdmin):
    form = NewsUpdateForm
    change_form_template = 'admin/newsportal/newsupdate/change_form.html'
    readonly_fields = ('published_date', 'updated_at')
    list_display = (
        'title',
        'category',
        'is_active',
        'published_date',
        'updated_at',
        'last_date',
    )
    list_display_links = ('title',)
    list_editable = ('is_active',)
    list_filter = ('category', 'is_active')
    date_hierarchy = 'published_date'
    search_fields = (
        'title',
        'short_description',
        'full_description',
        'organization',
    )
    ordering = ('-published_date', '-updated_at', '-pk')
    list_per_page = 25
    fieldsets = (
        (
            'Basic Information / Basic update information',
            {
                'fields': (
                    'title',
                    'organization',
                    'short_description',
                ),
            },
        ),
        (
            'Category and Classification',
            {
                'fields': ('category',),
            },
        ),
        (
            'Important Dates',
            {
                'fields': ('last_date', 'important_dates'),
            },
        ),
        (
            'Eligibility and Requirements',
            {
                'fields': (
                    'eligibility',
                    'age_limit',
                    'application_fee',
                    'total_vacancies',
                    'selection_process',
                ),
            },
        ),
        (
            'Description and Instructions / Full details',
            {
                'fields': ('full_description',),
            },
        ),
        (
            'Official Links',
            {
                'fields': ('official_link',),
            },
        ),
        (
            'Publishing Status',
            {
                'description': (
                    'The publication date is recorded automatically when '
                    'the item is first created. Publishing a draft later '
                    'does not change that existing date.'
                ),
                'fields': ('is_active', 'published_date', 'updated_at'),
            },
        ),
    )

    def get_urls(self):
        custom_urls = [
            path(
                '<path:object_id>/preview/',
                self.admin_site.admin_view(self.preview_view),
                name='newsportal_newsupdate_preview',
            ),
        ]
        return custom_urls + super().get_urls()

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        category = request.GET.get('category')
        valid_categories = {
            value for value, _label in NewsUpdate.CATEGORY_CHOICES
        }
        if category in valid_categories:
            initial['category'] = category
        return initial

    def save_model(self, request, obj, form, change):
        if '_save_draft' in request.POST:
            obj.is_active = False
        elif '_publish' in request.POST:
            obj.is_active = True
        super().save_model(request, obj, form, change)

    def preview_view(self, request, object_id):
        update = self.get_object(request, object_id)
        if update is None:
            raise Http404('Update not found')
        if not self.has_view_or_change_permission(request, update):
            raise PermissionDenied

        from .views import render_update_detail

        return render_update_detail(request, update, admin_preview=True)
