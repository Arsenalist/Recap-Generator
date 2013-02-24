from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'recaphack.truehoop.views.home', name='domain'),
    url(r'^truehoop$', 'recaphack.truehoop.views.home', name='home'),
    url(r'^truehoop/teams$', 'recaphack.truehoop.views.teams', name='teams'),
    url(r'^truehoop/lines$', 'recaphack.truehoop.views.lines', name='lines'),
    url(r'^truehoop/markup$', 'recaphack.truehoop.views.markup', name='markup'),
    url(r'^truehoop/preview$', 'recaphack.truehoop.views.preview', name='preview'),
    url(r'^truehoop/t$', 'recaphack.truehoop.views.t', name='t'),
    # url(r'^recaphack/', include('recaphack.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
