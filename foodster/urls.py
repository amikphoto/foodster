"""
URL configuration for foodster project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path as url
# from core.views import DishAutocomplete, TypeOfKitchenAutocomplete
# from core.views import display_cafes, delete_cafe, add_cafe
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog
# from crudbuilder import urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    # path(r'^', include('djangocms_forms.urls')),
    # path(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    path('', include('core.urls')),
    # path('rating/', include('rating.urls')),
    # url(r'^photologue/', include('photologue.urls',namespace='photologue')),
    # path('gallery/', include('gallery.urls')),
    path('system/', include('system.urls')),
    # url(r'^dish-autocomplete/$', DishAutocomplete.as_view(create_field='title'), name='dish-autocomplete'),
    # url(r'^typeofkitchen-autocomplete/$', TypeOfKitchenAutocomplete.as_view(create_field='title'), name='typeofkitchen-autocomplete'),
    path(
        'jsi18n/',
        cache_page(3600)(JavaScriptCatalog.as_view(packages=['formset'])),
        name='javascript-catalog'
    ),
    # url(r'^crud/', include(urls)),

]


if settings.DEBUG:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
# if settings.DEBUG:
    # import debug_toolbar
    # urlpatterns = [
    #     path('__debug__/', include(debug_toolbar.urls)),
    # ] + urlpatterns


urlpatterns.append(path('', include('cms.urls')))

# the new django admin sidebar is bad UX in django CMS custom admin views.
# admin.site.enable_nav_sidebar = False

