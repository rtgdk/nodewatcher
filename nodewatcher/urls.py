from django.conf import settings, urls
from django.conf.urls import static
from django.contrib import admin

# Importing nodewatcher.core.frontend.urls auto-discovers frontend components.
from nodewatcher.core.api import urls as api_urls
from nodewatcher.core.frontend import urls as frontend_urls

admin.autodiscover()

urlpatterns = [
    # Registry.
    urls.url(r'^registry/', urls.include('nodewatcher.core.registry.urls', namespace='registry', app_name='registry')),

    # API.
    urls.url(r'^api/v2/', urls.include(api_urls.v2_api.urls, namespace='apiv2', app_name='apiv2')),
    urls.url(r'^api/', urls.include(api_urls.v1_api.urls, namespace='api', app_name='api')),

    # Django admin interface.
    urls.url(r'^admin/', urls.include(admin.site.urls)),

    # Frontend.
    urls.url(r'^', urls.include(frontend_urls)),
]

if settings.DEBUG:
    from missing import views as missing_views
    from django.views import defaults

    urlpatterns += [
        # See CSRF_FAILURE_VIEW in settings.py as well.
        urls.url(r'^403/$', missing_views.forbidden_view),
        urls.url(r'^404/$', defaults.page_not_found),
        urls.url(r'^500/$', defaults.server_error),
    ]

if settings.DEBUG:
    # Serve static files in DEBUG mode.
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
