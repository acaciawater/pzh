from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from views import HomeView, well_locations, PopupView

admin.autodiscover()

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^data/', include('acacia.data.urls',namespace='acacia')),
    url(r'^net/', include('acacia.meetnet.urls',namespace='meetnet')),
    url(r'^val/', include('acacia.validation.urls',namespace='validation')),
    url(r'^locs/',well_locations,name='locs'),
    url(r'^pop/(?P<pk>\d+)', PopupView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.EXPORT_URL, document_root=settings.EXPORT_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
