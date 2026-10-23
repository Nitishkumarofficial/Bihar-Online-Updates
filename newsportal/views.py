from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from .forms import UpdateSearchForm
from .models import NewsUpdate


def _updates_context(request, page_size):
    search_form = UpdateSearchForm(request.GET)
    updates = NewsUpdate.objects.filter(is_active=True).order_by(
        '-published_date',
        '-pk',
    )

    if search_form.is_valid():
        filters = search_form.cleaned_data
        for term in filters['q'].split():
            updates = updates.filter(
                Q(title__icontains=term)
                | Q(short_description__icontains=term)
            )
        if filters['category']:
            updates = updates.filter(category=filters['category'])
        if filters['published_after']:
            updates = updates.filter(
                published_date__gte=filters['published_after']
            )
        if filters['published_before']:
            updates = updates.filter(
                published_date__lte=filters['published_before']
            )
    else:
        updates = updates.none()

    paginator = Paginator(updates, page_size)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)
    querystring = query_params.urlencode()
    filters_active = any(
        request.GET.get(name)
        for name in ('q', 'category', 'published_after', 'published_before')
    )

    return {
        'updates': page_obj,
        'page_obj': page_obj,
        'search_form': search_form,
        'querystring': querystring,
        'filters_active': filters_active,
        'total_count': paginator.count,
    }


def home(request):
    context = _updates_context(request, 9)
    context['social_links'] = settings.SOCIAL_LINKS
    return render(request, 'newsportal/home.html', context)


def all_updates(request):
    return render(
        request,
        'newsportal/updates_list.html',
        _updates_context(request, 12),
    )


def render_update_detail(request, update, admin_preview=False):
    share_url = request.build_absolute_uri(update.get_absolute_url())
    share_title = update.title
    share_text = f'{share_title}\n{share_url}'
    share_links = {
        'whatsapp': (
            'https://wa.me/?'
            + urlencode({'text': share_text})
        ),
        'telegram': (
            'https://t.me/share/url?'
            + urlencode({'url': share_url, 'text': share_title})
        ),
        'facebook': (
            'https://www.facebook.com/sharer/sharer.php?'
            + urlencode({'u': share_url})
        ),
        'x': (
            'https://twitter.com/intent/tweet?'
            + urlencode({'url': share_url, 'text': share_title})
        ),
        'linkedin': (
            'https://www.linkedin.com/sharing/share-offsite/?'
            + urlencode({'url': share_url})
        ),
    }
    related_updates = (
        NewsUpdate.objects.filter(is_active=True, category=update.category)
        .exclude(pk=update.pk)
        .order_by('-published_date', '-pk')[:3]
    )
    context = {
        'update': update,
        'related_updates': related_updates,
        'share_url': share_url,
        'share_title': share_title,
        'share_links': share_links,
        'admin_preview': admin_preview,
    }
    return render(request, 'newsportal/update_detail.html', context)


def update_detail(request, pk, slug=None):
    update = get_object_or_404(NewsUpdate, pk=pk, is_active=True)
    return render_update_detail(request, update)


def legacy_job_update(request):
    update = NewsUpdate.objects.filter(
        is_active=True,
        category='job',
    ).order_by('-published_date', '-pk').first()
    if update:
        return redirect(update.get_absolute_url())
    return render(request, 'newsportal/legacy/updates-2.html')


def site_info(request, section):
    pages = {
        'about': {
            'title': 'About Bihar Online Updates',
            'intro': (
                'Bihar Online Updates par published jobs, results, '
                'scholarships, admissions aur schemes ko category ke '
                'hisab se browse kiya ja sakta hai.'
            ),
            'details': (
                'Har update ki detail page par wahi jankari dikhayi jati '
                'hai jo website ke Admin mein publish ki gayi ho. Jahan '
                'official link diya ho, us link se original notice check karein.'
            ),
        },
        'contact': {
            'title': 'Contact and social pages',
            'intro': (
                'Social page ya channel par message bhejne ke liye neeche '
                'diye gaye Bihar Online Updates links ka use karein.'
            ),
            'details': (
                'Official notice ya application ke sawalon ke liye sambandhit '
                'department ke official contact details dekhein.'
            ),
        },
        'privacy': {
            'title': 'Privacy information',
            'intro': (
                'Public updates browse karne, search karne aur filter karne '
                'ke liye visitor account banana zaroori nahi hai.'
            ),
            'details': (
                'Admin login sirf authorized site administrators ke liye hai. '
                'Hosting provider ke standard technical logs uski apni policy '
                'ke mutabik process ho sakte hain. Is site par public update '
                'search ke liye personal details maangi nahi jati.'
            ),
        },
        'disclaimer': {
            'title': 'Disclaimer',
            'intro': (
                'Yeh website updates ko aasani se browse karne ke liye '
                'publish karti hai; yeh kisi government department ki '
                'official website nahi hai.'
            ),
            'details': (
                'Vacancy, dates, fees, eligibility aur results ko sambandhit '
                'official notification ya department website par verify karein. '
                'Application karne se pehle original notice zaroor padhein.'
            ),
        },
    }
    page = pages.get(section)
    if page is None:
        raise Http404('Information page not found')
    return render(
        request,
        'newsportal/site_info.html',
        {
            'page': page,
            'social_links': settings.SOCIAL_LINKS,
        },
    )
