import django_tables2 as tables
from .models import DishLibraryModel, CafeModel, VisitModel, DishModel, TypeOfKitchen, CulinaryClassModel
from django.utils.html import format_html
from django.urls import reverse
from django_tables2.utils import A

def item_data(**kwargs):
    id_item = kwargs.get('record')
    if id_item is None:
        return id_item
    else:
        return "/dishes/"+str(id_item.pk)

def item_cafe_data(**kwargs):
    id_item = kwargs.get('record')
    if id_item is None:
        return id_item
    else:
        return "/cafes/"+str(id_item.pk)

def item_data_visit(**kwargs):
    id_item = kwargs.get('record')
    cafe = kwargs.get('table').request.path
    if id_item is None:
        return id_item
    else:
        return cafe + str(id_item.pk)


class ClassTable(tables.Table):
    name = tables.Column(verbose_name='Название',
    )
    button = tables.TemplateColumn(verbose_name='Кнопка',
                                  template_name='django_tables2/class_button.html',
                                  orderable=False)  # orderable not sortable

    class Meta:
        model = CulinaryClassModel
        template_name = "django_tables2/bootstrap5.html"
        fields = ['name',]
        attrs = {"tbody":
                     {"hx-target":"closest tr",
                      "hx-swap":"outerHTML",
                      }}


class TypeTable(tables.Table):
    name = tables.Column(verbose_name='Название',
    )
    button = tables.TemplateColumn(verbose_name='Кнопка',
                                  template_name='django_tables2/type_button.html',
                                  orderable=False)  # orderable not sortable

    class Meta:
        model = TypeOfKitchen
        template_name = "django_tables2/bootstrap.html"
        fields = ['name',]
        attrs = {"tbody":
                     {"hx-target":"closest tr",
                      "hx-swap":"outerHTML",
                      }}

class BestDishesTable(tables.Table):
    dish_fk__name = tables.Column(verbose_name='Наименование блюда',
                                )
    group_count =  tables.Column(verbose_name='Количество',
                                )
    group_average = tables.Column(verbose_name='Средний балл',
                                )
    visit_fk__cafe_fk__title = tables.Column(verbose_name='Название кафе',
                    linkify=lambda record: "/cafe/"+str(record.get('visit_fk__cafe_fk')),
                                )

    # cafe_link = tables.LinkColumn(
    #     viewname='cafe',
    #     accessor='visit_fk__cafe_fk__title',  # Для словарей
    #     args=[tables.A('visit_fk__cafe_fk')],
    #     verbose_name='Кафе'
    # )


    class Meta:
        model = DishModel
        template_name = "django_tables2/bootstrap5_bestdishes.html"
        fields = ['dish_fk__name','visit_fk__cafe_fk__title','group_count','group_average']



class DishesTable(tables.Table):
    # id = tables.LinkColumn(text="Id", args=[A("pk")])
    # item = tables.TemplateColumn('<a href="/dishes/{{record.id}}">Edit</a>')
    # title = tables.Column(attrs={"td":
    #      {"hx-get": item_data,
    #       "hx-target": "#modaldialog",
    #       "data-bs-toggle": "modal",
    #       "data-bs-target": "#modaldialog",
    #       }})
    # id = tables.LinkColumn(text=lambda record: record.dish_fk, args=[A("pk")])
    id = tables.Column(verbose_name='Название блюда', accessor='dish_fk' , linkify=lambda record: record.get_absolute_url())

    rating = tables.TemplateColumn(verbose_name='Рейтинг', template_name="stars.html")
    # dish_fk = tables.LinkColumn()

    class Meta:
        model = DishModel
        template_name = "django_tables2/bootstrap5_dishes.html"
        # fields = {
        #     'title': ['exact', 'icontains'],
        #     ("title", "dishcatalog_fk", "type_of_kitchen_fk")
        # }
        fields = ['id','rating','rating2']


class CafesTable(tables.Table):

    title = tables.Column(linkify=lambda record: record.get_absolute_url()+"?way=list"
        # attrs={"td":
        #  {"hx-get": item_cafe_data,
        #   "hx-target": "#modaldialog",
        #   "data-bs-toggle": "modal",
        #   "data-bs-target": "#modaldialog",
        #   }}
    )

    typeofkitchen = tables.LinkColumn()

    class Meta:
        model = CafeModel
        template_name = "django_tables2/bootstrap5-cafes.html"
        fields = ['title', 'typeofkitchen','average_rating']


class VisitsTable(tables.Table):

    # data = tables.Column(attrs={"td":
    #      {"hx-get": item_data_visit,
    #
    #        "hx-target": "#cab",
    #       }})
    data = tables.Column(linkify=lambda record: record.get_absolute_url()+"?way=list")
    description = tables.Column(linkify=lambda record: record.get_absolute_url())


    # data = tables.LinkColumn(args=[A("pk")])

    class Meta:
        model = VisitModel
        template_name = "django_tables2/bootstrap5_visits.html"
        fields = ['data', 'description', 'average_dish_rating']

class MyVisitsTable(tables.Table):

    # data = tables.Column(attrs={"td":
    #      {"hx-get": item_data_visit,
    #
    #        "hx-target": "#cab",
    #       }})
    data = tables.Column(linkify=lambda record: record.get_absolute_url()+"?way=list")
    cafe_fk__title = tables.LinkColumn()
    description = tables.Column(linkify=lambda record: record.get_absolute_url())


    # data = tables.LinkColumn(args=[A("pk")])

    class Meta:
        model = VisitModel
        template_name = "django_tables2/bootstrap5_myvisits.html"
        fields = ['data', 'cafe_fk__title', 'description', 'average_dish_rating']
        order_by = '-data'