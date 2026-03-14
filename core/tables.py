import django_tables2 as tables
from .models import DishLibraryModel, CafeModel, VisitModel, DishModel, TypeOfKitchen, CulinaryClassModel, \
    DishImageModel, DishCatalog
from django.utils.safestring import mark_safe
from easy_thumbnails.files import get_thumbnailer
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

    # Новый столбец для изображений
    image = tables.Column(verbose_name="Изображение", empty_values=())

    def render_image(self, value, record):
        # Получаем первое изображение для данного блюда
        first_image = DishImageModel.objects.filter(dish_fk__dish_fk=record['dish_fk']).last()
        if first_image:
            thumbnailer = get_thumbnailer(first_image.image)
            thumbnail = thumbnailer.get_thumbnail({'size': (500, 500), 'crop': True})
            return mark_safe(f'<div class="col-12"><a href="/dishesphotos/{record["dish_fk"]}"><img src="{thumbnail.url}" class="img-fluid rounded" alt="Dish Image"></a></div>')
        return mark_safe('<div class="col-12"><img src="/media/media/no_photo.jpg" alt="No Image" class="img-fluid rounded"></div>')

    dish_info = tables.Column(verbose_name='Блюдо/Кафе',
                              accessor='dish_fk',
                              attrs={'td': {'class': 'd-md-none'},
                                     'th': {'class': 'd-md-none'}
                                     },
                              )

    def render_dish_info(self, value, record):
        dish_name = record.get('dish_fk__name', 'Не указано')
        cafe_name = record.get('visit_fk__cafe_fk__title', 'Не указано')
        dish_url = "/visitlist/" + str(record.get('dish_fk'))
        cafe_url = "/cafe/"+str(record.get('visit_fk__cafe_fk'))
        return mark_safe(f"""
            <div>
                <strong>Блюдо:</strong><a href='{dish_url}'>{dish_name}</a><br>
                <strong>Кафе:</strong><a href='{cafe_url}'> {cafe_name}</a>
            </div>
        """)

    dish_fk__name = tables.Column(verbose_name='Наименование блюда',
                                  attrs={'td': {'class':'d-none d-md-table-cell'},
                                         'th': {'class':'d-none d-md-table-cell'}
                                         },
                                  linkify=lambda record: "/visitlist/" + str(record.get('dish_fk')),
                                  )
    group_count =  tables.Column(verbose_name='Количество',
                                )
    group_average = tables.Column(verbose_name='Средний балл',
                                )
    visit_fk = tables.Column(verbose_name='Визит',
                                )
    visit_fk__cafe_fk__title = tables.Column(verbose_name='Название кафе',
                                 attrs={'td': {'class': 'd-none d-md-table-cell'},
                                        'th': {'class': 'd-none d-md-table-cell'}
                                        },
                                 linkify=lambda record: "/cafe/"+str(record.get('visit_fk__cafe_fk')),
                                )

    class Meta:
        model = DishModel
        exclude = ['visit_fk']
        template_name = "django_tables2/bootstrap5_bestdishes.html"
        fields = ['image','dish_info','dish_fk__name','visit_fk__cafe_fk__title','group_count','group_average']


class DishesVisitTable(tables.Table):
    id = tables.Column(verbose_name='Название блюда', accessor='dish_fk' , linkify=lambda record: record.get_absolute_url())

    rating = tables.TemplateColumn(verbose_name='Рейтинг', template_name="stars.html")
    user = tables.Column(verbose_name='Критик',)

    class Meta:
        model = DishModel
        template_name = "django_tables2/bootstrap5_dishes.html"
        fields = ['id','rating','user']


class DishesTable(tables.Table):

    # visit_ids_list = tables.Column(
    #     verbose_name='ID визитов',
    #     accessor='visit_ids_list',
    #     orderable=False,
    #     attrs={
    #         'td': {'class': 'text-muted'},
    #         'th': {'class': 'text-center'}
    #     }
    # )

    name = tables.Column(
        verbose_name='Название блюда',
        accessor='dish_fk__name',
        # linkify=lambda record: "/visitlist/" + str(record.visit_ids_list),
    )

    # Количество посещений
    dish_count = tables.Column(
        verbose_name='Визиты',
        accessor='dish_count'
    )

    visit_links = tables.TemplateColumn(
        verbose_name='Визиты',
        template_name="django_tables2/visit_links.html",
        orderable=False,
        attrs={'td': {'class': 'text-center'}}
    )

    # Средний рейтинг (числом)
    avg_rating = tables.Column(
        verbose_name='Средний рейтинг',
        accessor='avg_rating',
    )

    # Звезды рейтинга (шаблон) - БЕЗ extra_context
    stars = tables.TemplateColumn(
        verbose_name='Рейтинг',
        template_name="aver_stars.html",
        accessor='avg_rating'  # ← Передаёт значение в record.value
    )

    # Цена (диапазон)
    price_range = tables.Column(
        verbose_name='Цена',
        accessor='min_price',
    )

    class Meta:
        template_name = "django_tables2/bootstrap5_dishes.html"
        fields = ['name', 'visit_links', 'dish_count', 'avg_rating', 'stars', 'price_range',]

    def render_price_range(self, value, record):
        if record['min_price'] and record['max_price']:
            if record['min_price'] == record['max_price']:
                return f"{record['min_price']} ₽"
            return f"от {record['min_price']} до {record['max_price']} ₽"
        return '—'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for row in self.rows:
        #     visit_ids = row.record.get('visit_ids', '')
        #     row.record['visit_ids_list'] = [int(x) for x in visit_ids.split(',')] if visit_ids else []
        for row in self.rows:
            visit_ids_list = []
            visit_dates_list = []

            if row.record.get('visit_ids'):
                ids = row.record['visit_ids'].split(',')
                dates = row.record.get('visit_dates', '').split(',') if row.record.get('visit_dates') else []

                for i, vid in enumerate(ids):
                    visit_ids_list.append({
                        'id': int(vid),
                        'date': dates[i] if i < len(dates) else None
                    })

            # Добавляем в record для доступа в шаблоне
            row.record['visit_ids_list'] = visit_ids_list
            row.record['visit_dates_list'] = visit_dates_list
            # row.record['cafe_id'] = self.cafe_id

class VisitsListTable(tables.Table):

    data = tables.DateTimeColumn(format='d E Y, H:i', linkify=lambda record: record.get_absolute_url()+"?way=list", attrs={"td": {"class": "plain-link"}})
    # description = tables.Column(linkify=lambda record: record.get_absolute_url())
    description = tables.Column()

    def render_description(self, record):
        text = getattr(record, 'description', '')
        max_length = 80
        if len(text) > max_length:
            return text[:max_length].rstrip() + "…"
        return text


    class Meta:
        model = VisitModel
        template_name = "django_tables2/bootstrap5_visits_list.html"
        fields = ['data', 'description','average_dish_rating','user','register']


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
    data = tables.DateTimeColumn(format='d E Y, H:i', linkify=lambda record: record.get_absolute_url()+"?way=list", attrs={"td": {"class": "plain-link"}})
    # description = tables.Column(linkify=lambda record: record.get_absolute_url())
    description = tables.Column()

    def render_description(self, record):
        text = getattr(record, 'description', '')
        max_length = 80
        if len(text) > max_length:
            return text[:max_length].rstrip() + "…"
        return text


    # data = tables.LinkColumn(args=[A("pk")])

    class Meta:
        model = VisitModel
        template_name = "django_tables2/bootstrap5_visits.html"
        fields = ['data', 'user', 'description', 'average_dish_rating']

class MyVisitsTable(tables.Table):

    # data = tables.Column(attrs={"td":
    #      {"hx-get": item_data_visit,
    #
    #        "hx-target": "#cab",
    #       }})
    description = tables.Column()

    def render_description(self, record):
        text = getattr(record, 'description', '')
        max_length = 80
        if len(text) > max_length:
            return text[:max_length].rstrip() + "…"
        return text

    data = tables.DateTimeColumn(format='d E Y, H:i', linkify=lambda record: record.get_absolute_url()+"?way=list", attrs={"td": {"class": "plain-link"}})
    # data = tables.Column(linkify=lambda record: record.get_absolute_url()+"?way=list")
    cafe_fk__title = tables.LinkColumn()
    # description = tables.Column(linkify=lambda record: record.get_absolute_url())


    # data = tables.LinkColumn(args=[A("pk")])

    class Meta:
        model = VisitModel
        template_name = "django_tables2/bootstrap5_myvisits.html"
        fields = ['data', 'cafe_fk__title', 'description', 'average_dish_rating']
        order_by = '-data'


class TypesOfCuisineTable(tables.Table):
    cafe_fk = tables.Column(linkify=lambda record: reverse('core:cafe_cab', kwargs={'pk': record.cafe_fk_id}))

    class Meta:
        model = DishLibraryModel
        template_name = "django_tables2/bootstrap5_сuisine.html"
        fields = ['cafe_fk', 'name', 'type_of_kitchen_fk']


class DishesCatTable(tables.Table):
    class Meta:
        model = DishCatalog
        template_name = "django_tables2/bootstrap.html"
