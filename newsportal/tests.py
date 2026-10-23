from datetime import date
from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import NewsUpdate


class HomePageTests(TestCase):
    def test_homepage_renders_django_template_and_static_assets(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsportal/home.html')
        self.assertRegex(
            response.content.decode(),
            r'/static/newsportal/style\.[\w]+\.css',
        )
        self.assertRegex(
            response.content.decode(),
            r'/static/newsportal/script\.[\w]+\.js',
        )
        self.assertNotContains(response, '{% load static %}')

    def test_homepage_shows_active_updates_newest_first(self):
        older_update = NewsUpdate.objects.create(
            title='Older active update',
            category='job',
            short_description='Older description',
        )
        newer_update = NewsUpdate.objects.create(
            title='Newer active update',
            category='scholarship',
            short_description='Newer description',
            last_date=date(2026, 11, 30),
            official_link='https://example.com/notice',
        )
        NewsUpdate.objects.filter(pk=older_update.pk).update(
            published_date=date(2026, 10, 1)
        )
        NewsUpdate.objects.filter(pk=newer_update.pk).update(
            published_date=date(2026, 10, 2)
        )
        NewsUpdate.objects.create(
            title='Inactive update',
            category='result',
            short_description='This must not be displayed',
            is_active=False,
        )

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertLess(
            content.index('Newer active update'),
            content.index('Older active update'),
        )
        self.assertContains(response, 'Scholarships')
        self.assertContains(response, 'Last date:')
        self.assertContains(response, '30, 2026')
        self.assertContains(response, 'https://example.com/notice')
        self.assertNotContains(response, 'Inactive update')

    def test_view_all_updates_lists_active_admin_updates_and_detail_links(self):
        visible_job = NewsUpdate.objects.create(
            title='Admin added fresh recruitment',
            category='job',
            short_description='Verified recruitment details',
        )
        visible_scheme = NewsUpdate.objects.create(
            title='Admin added student scheme',
            category='scheme',
            short_description='Verified scheme details',
        )
        NewsUpdate.objects.create(
            title='Inactive job not public',
            category='job',
            short_description='Must not appear in view all',
            is_active=False,
        )

        response = self.client.get(reverse('legacy-all-updates'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, visible_job.title)
        self.assertContains(response, visible_scheme.title)
        self.assertContains(response, visible_job.get_absolute_url())
        self.assertContains(response, 'पूरी जानकारी देखें / Read More')
        self.assertNotContains(response, 'Inactive job not public')

    def test_view_all_updates_search_category_and_pagination(self):
        for index in range(13):
            NewsUpdate.objects.create(
                title=f'Bihar admin job update {index}',
                category='job',
                short_description='Published vacancy.',
            )
        NewsUpdate.objects.create(
            title='Bihar admin scholarship',
            category='scholarship',
            short_description='Published scholarship.',
        )

        response = self.client.get(
            reverse('legacy-all-updates'),
            {'q': 'Bihar admin', 'category': 'job'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.count, 13)
        self.assertContains(response, 'category=job&amp;page=2')
        self.assertNotContains(response, 'Bihar admin scholarship')

        next_page = self.client.get(
            reverse('legacy-all-updates'),
            {'q': 'Bihar admin', 'category': 'job', 'page': '2'},
        )

        self.assertEqual(next_page.context['page_obj'].number, 2)
        self.assertContains(next_page, 'Bihar admin job update 0')

    def test_homepage_shows_empty_state_when_there_are_no_active_updates(self):
        NewsUpdate.objects.create(
            title='Inactive update',
            category='other',
            short_description='Not visible on the homepage',
            is_active=False,
        )

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No updates found')
        self.assertContains(response, 'Reset Filters')
        self.assertContains(response, 'href="/admin/"')

    def test_homepage_category_cards_and_buttons_link_to_filtered_updates(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        for category in (
            'job',
            'scholarship',
            'result',
            'admission',
            'scheme',
            'other',
        ):
            with self.subTest(category=category):
                self.assertContains(
                    response,
                    f"{reverse('legacy-all-updates')}?category={category}",
                )

    def test_homepage_jobs_and_section_buttons_do_not_use_broken_relative_urls(self):
        response = self.client.get(reverse('home'))

        self.assertNotContains(response, 'href="all-updates.html"')
        self.assertNotContains(response, 'href="updates/updates-')

    def test_homepage_social_and_footer_links_have_working_destinations(self):
        response = self.client.get(reverse('home'))

        self.assertContains(
            response,
            'https://www.youtube.com/@Biharonlineupdatesofficial',
        )
        self.assertContains(
            response,
            'https://www.instagram.com/invites/contact/',
        )
        self.assertContains(
            response,
            'https://web.telegram.org/k/',
        )
        self.assertContains(
            response,
            'https://whatsapp.com/channel/0029VbDt7CgDzgTKd1cyM122',
        )
        self.assertContains(response, 'Join WhatsApp Channel')
        self.assertNotContains(response, 'class="youtube-btn" target="_blank"')
        self.assertNotContains(
            response,
            'class="social whatsapp" target="_blank"',
        )
        for section in ('about', 'contact', 'privacy', 'disclaimer'):
            with self.subTest(section=section):
                self.assertContains(response, reverse('site-info', args=[section]))

    def test_site_information_pages_render_and_unknown_page_returns_404(self):
        for section in ('about', 'contact', 'privacy', 'disclaimer'):
            with self.subTest(section=section):
                response = self.client.get(reverse('site-info', args=[section]))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'Back to home')
        self.assertEqual(
            self.client.get(reverse('site-info', args=['unknown'])).status_code,
            404,
        )

    def test_search_matches_titles_and_descriptions_and_combines_with_category(self):
        title_match = NewsUpdate.objects.create(
            title='Bihar teacher recruitment',
            category='job',
            short_description='Application details',
        )
        description_match = NewsUpdate.objects.create(
            title='New notification',
            category='job',
            short_description='Bihar teacher recruitment details',
        )
        NewsUpdate.objects.create(
            title='Bihar teacher scholarship',
            category='scholarship',
            short_description='Different category',
        )
        NewsUpdate.objects.create(
            title='Bihar teacher inactive',
            category='job',
            short_description='Not publicly available',
            is_active=False,
        )

        response = self.client.get(
            reverse('home'),
            {'q': 'Bihar teacher', 'category': 'job'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, title_match.title)
        self.assertContains(response, description_match.title)
        self.assertNotContains(response, 'Bihar teacher scholarship')
        self.assertNotContains(response, 'Bihar teacher inactive')
        self.assertContains(response, 'name="q" value="Bihar teacher"')
        self.assertContains(response, 'value="job" selected')

    def test_publication_date_filters_are_inclusive(self):
        included = NewsUpdate.objects.create(
            title='In date range',
            category='result',
            short_description='Included result',
        )
        excluded = NewsUpdate.objects.create(
            title='Outside date range',
            category='result',
            short_description='Excluded result',
        )
        NewsUpdate.objects.filter(pk=included.pk).update(
            published_date=date(2026, 10, 10)
        )
        NewsUpdate.objects.filter(pk=excluded.pk).update(
            published_date=date(2026, 10, 11)
        )

        response = self.client.get(
            reverse('home'),
            {
                'published_after': '2026-10-10',
                'published_before': '2026-10-10',
            },
        )

        self.assertContains(response, included.title)
        self.assertNotContains(response, excluded.title)

    def test_pagination_preserves_search_and_category_filters(self):
        for index in range(10):
            NewsUpdate.objects.create(
                title=f'Bihar teaching update {index}',
                category='job',
                short_description='Recruitment notice',
            )
        NewsUpdate.objects.create(
            title='Bihar teaching scholarship',
            category='scholarship',
            short_description='Matching keyword but wrong category',
        )

        first_page = self.client.get(
            reverse('home'),
            {'q': 'Bihar teaching', 'category': 'job'},
        )

        self.assertEqual(first_page.context['page_obj'].paginator.count, 10)
        self.assertContains(
            first_page,
            '?q=Bihar+teaching&amp;category=job&amp;page=2#updates',
        )

        second_page = self.client.get(
            reverse('home'),
            {'q': 'Bihar teaching', 'category': 'job', 'page': '2'},
        )

        self.assertEqual(second_page.context['page_obj'].number, 2)
        self.assertContains(second_page, 'Bihar teaching update 0')
        self.assertNotContains(second_page, 'Bihar teaching scholarship')
        self.assertContains(
            second_page,
            '?q=Bihar+teaching&amp;category=job&amp;page=1#updates',
        )

    def test_empty_search_results_and_invalid_date_ranges(self):
        empty_response = self.client.get(
            reverse('home'),
            {'q': 'no matching update'},
        )

        self.assertContains(empty_response, 'No updates found')
        self.assertContains(empty_response, 'Reset Filters')

        invalid_response = self.client.get(
            reverse('home'),
            {
                'published_after': '2026-10-20',
                'published_before': '2026-10-01',
            },
        )

        self.assertContains(
            invalid_response,
            'End date must be on or after the start date.',
        )

    def test_user_entered_text_is_escaped(self):
        NewsUpdate.objects.create(
            title='<script>alert(1)</script>',
            category='other',
            short_description='<img src=x onerror=alert(1)>',
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertContains(
            response,
            '&lt;img src=x onerror=alert(1)&gt;',
        )
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_legacy_pages_and_admin_routes_remain_available(self):
        for route_name in (
            'legacy-update-1',
            'legacy-update-2',
            'legacy-update-3',
            'legacy-all-updates',
        ):
            response = self.client.get(reverse(route_name))
            self.assertEqual(response.status_code, 200)
            self.assertRegex(
                response.content.decode(),
                r'/static/newsportal/style\.[\w]+\.css',
            )

        admin_response = self.client.get(reverse('admin:index'))
        self.assertEqual(admin_response.status_code, 302)
        self.assertEqual(
            admin_response.url,
            f"{reverse('admin:login')}?next={reverse('admin:index')}",
        )

    def test_updates_created_in_admin_are_filtered_on_homepage(self):
        admin_user = get_user_model().objects.create_superuser(
            username='test-admin',
            email='test-admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin_user)
        add_url = reverse('admin:newsportal_newsupdate_add')
        active_update = {
            'title': 'Admin-created active update',
            'category': 'job',
            'short_description': 'Visible from the homepage',
            'last_date': '',
            'official_link': 'https://example.com/active',
            'is_active': 'on',
            '_save': 'Save',
        }
        inactive_update = {
            'title': 'Admin-created inactive update',
            'category': 'result',
            'short_description': 'Must remain hidden',
            'last_date': '',
            'official_link': '',
            '_save': 'Save',
        }

        self.assertEqual(self.client.post(add_url, active_update).status_code, 302)
        self.assertEqual(self.client.post(add_url, inactive_update).status_code, 302)

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Admin-created active update')
        self.assertContains(response, 'https://example.com/active')
        self.assertNotContains(response, 'Admin-created inactive update')

    def test_admin_exposes_sections_for_full_update_details(self):
        admin_user = get_user_model().objects.create_superuser(
            username='details-admin',
            email='details-admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse('admin:newsportal_newsupdate_add'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Basic update information')
        self.assertContains(response, 'Full details')
        self.assertContains(response, 'full_description')
        self.assertContains(response, 'organization')
        self.assertContains(response, 'total_vacancies')
        self.assertContains(response, 'eligibility')
        self.assertContains(response, 'age_limit')
        self.assertContains(response, 'application_fee')
        self.assertContains(response, 'important_dates')
        self.assertContains(response, 'selection_process')

    def test_admin_saves_full_details_for_public_detail_page(self):
        admin_user = get_user_model().objects.create_superuser(
            username='full-details-admin',
            email='full-details-admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin_user)
        add_url = reverse('admin:newsportal_newsupdate_add')
        response = self.client.post(
            add_url,
            {
                'title': 'Verified recruitment notice',
                'category': 'job',
                'short_description': 'Short public summary.',
                'full_description': 'Complete verified notice text.',
                'organization': 'Official organization',
                'total_vacancies': '125',
                'eligibility': 'As specified in the verified notice.',
                'age_limit': 'As specified in the verified notice.',
                'application_fee': 'As specified in the verified notice.',
                'important_dates': 'Dates as specified in the verified notice.',
                'selection_process': 'As specified in the verified notice.',
                'last_date': '',
                'official_link': 'https://example.com/verified-notice',
                'is_active': 'on',
                '_save': 'Save',
            },
        )

        self.assertEqual(response.status_code, 302)
        update = NewsUpdate.objects.get(title='Verified recruitment notice')
        detail_response = self.client.get(update.get_absolute_url())

        self.assertContains(detail_response, 'Complete verified notice text.')
        self.assertContains(detail_response, 'Official organization')
        self.assertContains(detail_response, '125')
        self.assertContains(
            detail_response,
            'https://example.com/verified-notice',
        )

    def test_legacy_job_page_redirects_to_latest_active_job_detail(self):
        update = NewsUpdate.objects.create(
            title='Verified job listing',
            category='job',
            short_description='Verified job summary.',
        )

        response = self.client.get(reverse('legacy-update-2'))

        self.assertRedirects(response, update.get_absolute_url())

    def test_legacy_job_page_shows_empty_message_without_active_jobs(self):
        response = self.client.get(reverse('legacy-update-2'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Abhi koi active job update available nahi hai')


class UpdateDetailTests(TestCase):
    def test_detail_page_shows_stored_update_data_and_share_actions(self):
        update = NewsUpdate.objects.create(
            title='Bihar teacher recruitment',
            category='job',
            short_description='Eligibility and application details.\nRead the full notice.',
            full_description='Complete official job notification text.',
            organization='Bihar Public Service Commission',
            total_vacancies='Verified total: 42',
            eligibility='Degree specified by the official notice.',
            age_limit='Age criteria in official notice.',
            application_fee='Fee as per official notice.',
            important_dates='Application dates as per official notice.',
            selection_process='Written examination.',
            last_date=date(2026, 12, 15),
            official_link='https://example.com/official-notice',
        )
        related = NewsUpdate.objects.create(
            title='Another Bihar teaching vacancy',
            category='job',
            short_description='Related public notification.',
        )
        NewsUpdate.objects.create(
            title='Unpublished related vacancy',
            category='job',
            short_description='Not publicly available.',
            is_active=False,
        )
        NewsUpdate.objects.create(
            title='Unrelated scholarship',
            category='scholarship',
            short_description='Different category.',
        )

        response = self.client.get(update.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, update.title)
        self.assertContains(response, update.get_category_display())
        self.assertContains(response, update.published_date.strftime('%Y-%m-%d'))
        self.assertContains(response, 'Last updated:')
        self.assertContains(response, 'Complete official job notification text.')
        self.assertContains(response, 'Bihar Public Service Commission')
        self.assertContains(response, 'Verified total: 42')
        self.assertContains(response, 'Degree specified by the official notice.')
        self.assertContains(response, 'Age criteria in official notice.')
        self.assertContains(response, 'Fee as per official notice.')
        self.assertContains(response, 'Application dates as per official notice.')
        self.assertContains(response, 'Written examination.')
        self.assertContains(response, 'Last date:')
        self.assertContains(response, 'https://example.com/official-notice')
        self.assertContains(response, 'data-share-platform="whatsapp"')
        self.assertContains(response, 'id="copyUpdateLink"')
        self.assertContains(response, 'id="nativeShareUpdate"')
        self.assertContains(response, 'href="https://t.me/share/url?')
        self.assertContains(response, 'facebook.com/sharer/sharer.php')
        self.assertContains(response, 'twitter.com/intent/tweet')
        self.assertContains(response, 'linkedin.com/sharing/share-offsite')
        share_url = response.context['share_url']
        self.assertEqual(
            share_url,
            f'http://testserver{update.get_absolute_url()}',
        )
        telegram_href = response.context['share_links']['telegram']
        telegram_params = parse_qs(urlparse(telegram_href).query)
        self.assertEqual(telegram_params['url'], [share_url])
        self.assertEqual(telegram_params['text'], [update.title])
        whatsapp_href = response.context['share_links']['whatsapp']
        whatsapp_params = parse_qs(urlparse(whatsapp_href).query)
        self.assertEqual(whatsapp_params['text'], [f'{update.title}\n{share_url}'])
        self.assertContains(response, related.title)
        self.assertNotContains(response, 'Unpublished related vacancy')
        self.assertNotContains(response, 'Unrelated scholarship')

    def test_detail_url_remains_valid_if_the_title_changes(self):
        update = NewsUpdate.objects.create(
            title='Original update title',
            category='job',
            short_description='Public notice.',
        )
        original_url = update.get_absolute_url()
        update.title = 'Updated title'
        update.save()

        response = self.client.get(original_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Updated title')

    def test_detail_page_escapes_user_text(self):
        update = NewsUpdate.objects.create(
            title='<script>alert(1)</script>',
            category='other',
            short_description='<img src=x onerror=alert(1)>',
        )

        response = self.client.get(update.get_absolute_url())

        self.assertContains(response, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertContains(
            response,
            '&lt;img src=x onerror=alert(1)&gt;',
        )
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_social_share_links_encode_title_and_absolute_page_url(self):
        update = NewsUpdate.objects.create(
            title='Teacher & Clerk भर्ती / 2026?',
            category='job',
            short_description='Public details.',
        )

        response = self.client.get(update.get_absolute_url())
        share_url = f'http://testserver{update.get_absolute_url()}'
        expected_links = response.context['share_links']

        for platform, expected_host in (
            ('whatsapp', 'wa.me'),
            ('telegram', 't.me'),
            ('facebook', 'www.facebook.com'),
            ('x', 'twitter.com'),
            ('linkedin', 'www.linkedin.com'),
        ):
            with self.subTest(platform=platform):
                parsed_link = urlparse(expected_links[platform])
                self.assertEqual(parsed_link.scheme, 'https')
                self.assertEqual(parsed_link.netloc, expected_host)

        whatsapp_params = parse_qs(urlparse(expected_links['whatsapp']).query)
        self.assertEqual(
            whatsapp_params['text'],
            [f'{update.title}\n{share_url}'],
        )
        telegram_params = parse_qs(urlparse(expected_links['telegram']).query)
        self.assertEqual(telegram_params['url'], [share_url])
        self.assertEqual(telegram_params['text'], [update.title])
        facebook_params = parse_qs(urlparse(expected_links['facebook']).query)
        self.assertEqual(facebook_params['u'], [share_url])
        x_params = parse_qs(urlparse(expected_links['x']).query)
        self.assertEqual(x_params['url'], [share_url])
        self.assertEqual(x_params['text'], [update.title])
        linkedin_params = parse_qs(urlparse(expected_links['linkedin']).query)
        self.assertEqual(linkedin_params['url'], [share_url])

    def test_unpublished_and_missing_updates_return_404(self):
        unpublished = NewsUpdate.objects.create(
            title='Private update',
            category='job',
            short_description='Not public.',
            is_active=False,
        )

        self.assertEqual(
            self.client.get(unpublished.get_absolute_url()).status_code,
            404,
        )
        self.assertEqual(self.client.get('/updates/999999/missing/').status_code, 404)

    @override_settings(DEBUG=False)
    def test_missing_update_uses_helpful_404_template(self):
        response = self.client.get('/updates/999999/missing/')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Update not found', status_code=404)
        self.assertContains(response, 'not publicly available', status_code=404)

    def test_homepage_links_to_the_update_detail_route(self):
        update = NewsUpdate.objects.create(
            title='Bihar result notice',
            category='result',
            short_description='Published result details.',
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, update.get_absolute_url())
        self.assertContains(response, 'पूरी जानकारी देखें / Read More')
        self.assertContains(response, 'class="read-detail-link"')

    def test_job_fields_are_hidden_when_blank_and_not_rendered_for_other_categories(self):
        job = NewsUpdate.objects.create(
            title='Job without supplied details',
            category='job',
            short_description='Only verified summary.',
        )
        scholarship = NewsUpdate.objects.create(
            title='Scholarship details',
            category='scholarship',
            short_description='Scholarship summary.',
            eligibility='As stated in the notice.',
            age_limit='This field should not show for scholarships.',
            application_fee='This fee is not relevant to this scholarship.',
        )

        job_response = self.client.get(job.get_absolute_url())
        scholarship_response = self.client.get(scholarship.get_absolute_url())

        self.assertNotContains(job_response, 'Total vacancies')
        self.assertNotContains(job_response, 'Age limit')
        self.assertContains(scholarship_response, 'Eligibility')
        self.assertNotContains(scholarship_response, 'Age limit')
        self.assertNotContains(scholarship_response, 'Application fee')


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username='dashboard-admin',
            email='dashboard-admin@example.com',
            password='test-password',
        )
        self.client.force_login(self.admin_user)

    def test_dashboard_shows_database_counts_and_correct_navigation(self):
        NewsUpdate.objects.create(
            title='Published job',
            category='job',
            short_description='Public job.',
        )
        NewsUpdate.objects.create(
            title='Draft job',
            category='job',
            short_description='Private job.',
            is_active=False,
        )
        NewsUpdate.objects.create(
            title='Published scholarship',
            category='scholarship',
            short_description='Public scholarship.',
        )

        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['dashboard_stats'],
            {
                'total': 3,
                'jobs': 2,
                'scholarships': 1,
                'schemes': 0,
                'results': 0,
                'admissions': 0,
                'drafts': 1,
                'published': 2,
            },
        )
        self.assertContains(response, 'Total Updates')
        self.assertContains(response, 'Government Schemes')
        self.assertContains(response, reverse('home'))
        self.assertContains(
            response,
            reverse('admin:newsportal_newsupdate_changelist')
            + '?category__exact=job',
        )
        self.assertContains(
            response,
            reverse('admin:auth_user_changelist'),
        )
        self.assertContains(response, 'are static and are not populated')

    def test_quick_add_actions_open_the_correct_category_form(self):
        response = self.client.get(reverse('admin:index'))

        for category in (
            'job',
            'scholarship',
            'scheme',
            'result',
            'admission',
        ):
            with self.subTest(category=category):
                add_url = (
                    reverse('admin:newsportal_newsupdate_add')
                    + f'?category={category}'
                )
                self.assertContains(response, add_url)
                add_response = self.client.get(add_url)
                self.assertEqual(add_response.status_code, 200)
                self.assertEqual(
                    add_response.context['adminform'].form.initial['category'],
                    category,
                )

    def test_admin_form_has_clear_sections_help_and_date_widget(self):
        response = self.client.get(
            reverse('admin:newsportal_newsupdate_add')
            + '?category=job'
        )

        self.assertEqual(response.status_code, 200)
        for heading in (
            'Basic Information',
            'Category and Classification',
            'Important Dates',
            'Eligibility and Requirements',
            'Description and Instructions',
            'Official Links',
            'Publishing Status',
            'Where this update appears',
        ):
            with self.subTest(heading=heading):
                self.assertContains(response, heading)
        self.assertContains(response, 'type="date"')
        self.assertContains(response, 'Short description is used on')
        form = response.context['adminform'].form
        self.assertTrue(form.fields['title'].required)
        self.assertFalse(form.fields['official_link'].required)

    def test_draft_save_preview_publish_and_public_visibility(self):
        add_url = reverse('admin:newsportal_newsupdate_add')
        response = self.client.post(
            add_url,
            {
                'title': 'Draft preview recruitment',
                'category': 'job',
                'short_description': 'Short preview summary.',
                'full_description': 'Full private preview details.',
                'official_link': 'https://example.com/notice',
                'last_date': '',
                '_save_draft': 'Save as draft',
            },
        )
        self.assertEqual(response.status_code, 302)
        update = NewsUpdate.objects.get(title='Draft preview recruitment')
        self.assertFalse(update.is_active)
        self.assertEqual(
            self.client.get(update.get_absolute_url()).status_code,
            404,
        )

        preview_url = reverse(
            'admin:newsportal_newsupdate_preview',
            args=[update.pk],
        )
        preview = self.client.get(preview_url)
        self.assertEqual(preview.status_code, 200)
        self.assertContains(preview, 'Administrator preview')
        self.assertContains(preview, 'Full private preview details.')
        self.assertContains(
            preview,
            reverse('admin:newsportal_newsupdate_change', args=[update.pk]),
        )

        publish_response = self.client.post(
            reverse('admin:newsportal_newsupdate_change', args=[update.pk]),
            {
                'title': update.title,
                'category': update.category,
                'short_description': update.short_description,
                'full_description': update.full_description,
                'official_link': update.official_link,
                'last_date': '',
                '_publish': 'Publish',
            },
        )
        self.assertEqual(publish_response.status_code, 302)
        update.refresh_from_db()
        self.assertTrue(update.is_active)
        self.assertEqual(self.client.get(update.get_absolute_url()).status_code, 200)

    def test_preview_requires_admin_authentication(self):
        update = NewsUpdate.objects.create(
            title='Protected preview',
            category='result',
            short_description='Private until published.',
            is_active=False,
        )
        self.client.logout()

        response = self.client.get(
            reverse('admin:newsportal_newsupdate_preview', args=[update.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin:login'), response.url)

    def test_admin_search_and_category_status_filters_work(self):
        NewsUpdate.objects.create(
            title='Bihar filtered draft',
            category='job',
            short_description='Draft description.',
            is_active=False,
        )
        NewsUpdate.objects.create(
            title='Bihar filtered published',
            category='job',
            short_description='Published description.',
        )
        NewsUpdate.objects.create(
            title='Bihar scholarship',
            category='scholarship',
            short_description='Different category.',
            is_active=False,
        )

        response = self.client.get(
            reverse('admin:newsportal_newsupdate_changelist'),
            {
                'q': 'Bihar filtered',
                'category__exact': 'job',
                'is_active__exact': '0',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bihar filtered draft')
        self.assertNotContains(response, 'Bihar filtered published')
        self.assertNotContains(response, 'Bihar scholarship')

    def test_dashboard_hides_content_counts_from_staff_without_view_permission(self):
        update = NewsUpdate.objects.create(
            title='Private staff preview',
            category='job',
            short_description='Not available to add-only staff.',
            is_active=False,
        )
        staff_user = get_user_model().objects.create_user(
            username='add-only-staff',
            password='test-password',
            is_staff=True,
        )
        from django.contrib.auth.models import Permission

        staff_user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label='newsportal',
                codename='add_newsupdate',
            )
        )
        self.client.force_login(staff_user)

        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['dashboard_can_view_updates'])
        self.assertNotContains(response, 'Total Updates')
        self.assertContains(response, 'Add New Job')
        change_list_url = reverse(
            'admin:newsportal_newsupdate_changelist'
        )
        self.assertFalse(
            any(
                link['url'] == change_list_url
                for section in response.context['dashboard_navigation']
                for link in section['links']
            )
        )
        self.assertEqual(
            self.client.get(
                change_list_url
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    'admin:newsportal_newsupdate_preview',
                    args=[update.pk],
                )
            ).status_code,
            403,
        )
