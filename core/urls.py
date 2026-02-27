from django.conf import settings
from django.conf.urls.static import static
# from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.urls import re_path as url
# from crudbuilder import urls

# from core import views
from .views import (CafeFormsetView, VisitView, TestView, add_dish_library, TableView, dishinfo,
                    add_dish_lib, CafesListView, Cafe_cab, VisitsView, VisitCab,
                    DishesListView, add_new_dish, add_new_dish_collection, TypeDictListView,
                    DictView, TypeEditTableView, TypeDictUpdateListView, ClassDictListView, ClassDictUpdateListView,
                    ClassEditTableView, BestDishesListView, MyVisitsListView,
                    VisitsList, DishPhotosList, StartView, Privacy, StorytalesView
                    )
# from iommi import Form
# from core.models import DishModel
# from iommi.views import crud_views
# from core.models import CulinaryClassModel

app_name = 'core'
urlpatterns = [

    # path('',
    #      RedirectView.as_view(url='/dishes/', permanent=True), name='pages-root'),

    path('', StartView.as_view(), name='start'),
    path('cafes/', CafesListView.as_view(), name='cafes'),

    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^crud/', include(urls)),

    path('dictionaries/', DictView.as_view(), name='dicts'),
    path('dictionaries/types/', TypeDictListView.as_view(), name='types'),
    path('dictionaries/types/<int:tpk>/', TypeDictUpdateListView.as_view(), name='updatetypes'),
    path('edittype/<int:pk>/', TypeEditTableView.as_view(), name='edittype'),

    path('dictionaries/classes/', ClassDictListView.as_view(), name='classes'),
    path('dictionaries/classes/<int:cpk>/', ClassDictUpdateListView.as_view(), name='updateclasses'),
    path('editclass/<int:pk>/', ClassEditTableView.as_view(), name='editclass'),
    # path('iommi/', crud_views(model=CulinaryClassModel)),
    # path('iommi/', iommitest, name='iommi'),

    path('cafe/<int:pk>/', Cafe_cab.as_view(extra_context={'edit': True}), name='cafe_cab'),
    # path('cafe/<int:pk>/?way=list', Cafe_cab.as_view(), name='cafe_cab_list'),

    path('cafe/add_cafe/', Cafe_cab.as_view(extra_context={'add': True}), name='cafe_add'),

    # path('visits/', VisitsView.as_view(), name='visit'),
    path('visits/<int:pk>/', VisitsView.as_view(), name='visits'),

    path('cafe/<int:cpk>/<int:pk>/', VisitCab.as_view(), name='visit'),

    # path('visits/', VisitsView.as_view(), name='allvisits'),

    path('visitcab/<int:cpk>/', VisitCab.as_view(extra_context={'add': True}), name='visitcab'),

    path('disheslist/<int:vpk>/', DishesListView.as_view(), name='dishlist'),

    path('adddish/<int:vpk>/', add_new_dish_collection.as_view(), name='add_new_dish'),

    # path('cafe/<int:cpk>/<int:vpk>/<int:pk>/', add_new_dish.as_view(), name='dishes'),

    path('cafe/<int:cpk>/<int:vpk>/<int:pk>/', add_new_dish_collection.as_view(extra_context={'edit': True}), name='dishes'),

    path('dishinfo/', dishinfo, name='dishinfo'),

    path('dishes/', BestDishesListView.as_view(), name='bestdishes'),

    path('myvisits/', MyVisitsListView.as_view(), name='myvisits'),

    path('visitlist/<int:pk>/', VisitsList.as_view(), name='visitlist'),

    path('dishesphotos/<int:pk>/', DishPhotosList.as_view(), name='visitlist'),

    path('privacy/', Privacy.as_view(), name='visitlist'),

    path('storytales/<int:pk>/', StorytalesView.as_view(), name='storytales'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)