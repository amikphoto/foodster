import django_filters
from django.urls import reverse_lazy
# from django_select2.forms import Select2Widget
from .models import DishLibraryModel, DishCatalog, TypeOfKitchen, CafeModel, VisitModel, DishModel, TypeOfKitchen, CulinaryClassModel
from dal_select2.widgets import ModelSelect2
# from django_addanother.widgets import AddAnotherWidgetWrapper


class ClassFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по названию')
    # typeofkitchen = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по типу кухни')


    class Meta:
        model = CulinaryClassModel
        fields = ['name',]



class KitchenTypeFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по названию')
    # typeofkitchen = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по типу кухни')


    class Meta:
        model = TypeOfKitchen
        fields = ['name',]

class BestDishesFilterSet(django_filters.FilterSet):
    dish_fk = django_filters.CharFilter(field_name="dish_fk__name", lookup_expr='icontains', label='Фильтр по названию блюда')

    class Meta:
        model = DishModel
        fields = ['dish_fk']


class DishesFilterSet(django_filters.FilterSet):
    dish_fk = django_filters.CharFilter(field_name="dish_fk__title", lookup_expr='icontains', label='Фильтр по названию блюда')

    class Meta:
        model = DishModel
        fields = ['dish_fk']

class VisitsFilterSet(django_filters.FilterSet):
    # data = django_filters.DateFilter(lookup_expr='gte',label='Дата')
    # data = django_filters.DateFromToRangeFilter()
    data = django_filters.DateRangeFilter()
    description = django_filters.CharFilter(lookup_expr='icontains', label='Описание')

    class Meta:
        model = VisitModel
        fields = ['data','description']

class MyVisitsFilterSet(django_filters.FilterSet):
    # data = django_filters.DateFilter(lookup_expr='gte',label='Дата')
    # data = django_filters.DateFromToRangeFilter()
    data = django_filters.DateRangeFilter()
    cafe_fk__title = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по названию кафе')

    # description = django_filters.CharFilter(lookup_expr='icontains', label='Описание')

    class Meta:
        model = VisitModel
        fields = ['data', 'cafe_fk__title']


class CafesLibraryFilterSet(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по названию кафе')
    typeofkitchen = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по типу кухни')


    class Meta:
        model = CafeModel
        fields = ['title', 'typeofkitchen']


class DishLibraryFilterSet(django_filters.FilterSet):

    title = django_filters.CharFilter(lookup_expr='icontains', label='Фильтр по названию')
    dishcatalog_fk = django_filters.ModelChoiceFilter(queryset=DishCatalog.objects.all(),
                                                      lookup_expr='exact',
                                                      label='Фильтр по типу блюда',
                                                      widget=ModelSelect2(url='dish-autocomplete',
                                                                                   attrs={
                                                                                       'style':'width:100%'
                                                                                        }),
                                                      )
    type_of_kitchen_fk = django_filters.ModelChoiceFilter(queryset=TypeOfKitchen.objects.all(),
                                                      lookup_expr='exact',
                                                      widget=ModelSelect2(url='typeofkitchen-autocomplete',
                                                                                       attrs={
                                                                                           'style': 'width:100%'
                                                                                       }),
                                                          )

    class Meta:
        model = DishLibraryModel
        fields = ['title', 'dishcatalog_fk', 'type_of_kitchen_fk']
        # fields = {
        #     'title': ['icontains'],
        #     'dishcatalog_fk': ['exact'],
        # }

        # widgets = {
        #     'dishcatalog_fk' : autocomplete.ModelSelect2(
        #         url='dish-autocomplete',
        #         attrs={'style': 'width: 100%;'},
        #     )
                # AddAnotherWidgetWrapper(
                # autocomplete.ModelSelect2(),
                # reverse_lazy('core:add_dish_library'),
            # )
        # }