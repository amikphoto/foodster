from django import forms
from django.forms.models import ModelForm, ModelChoiceField, construct_instance, model_to_dict
from django.template.context_processors import request
from django.urls import reverse
from location_field.widgets import LocationWidget

from .models import CafeModel, VisitModel, DishModel, CafeImageModel, DishLibraryModel, DishCatalog, VisitImageModel, DishImageModel, CulinaryClassModel, TypeOfKitchen
from django.forms import inlineformset_factory, Textarea, SelectMultiple, fields
from django.forms.fields import IntegerField, FileField, CharField, ChoiceField, MultipleChoiceField, BooleanField
from django.forms.widgets import HiddenInput, RadioSelect, NumberInput, CheckboxSelectMultiple, Widget, ChoiceWidget, Select
from formset.widgets import DateInput, Selectize, SelectizeMultiple
from formset.collection import FormCollection
from formset.renderers.bootstrap import FormRenderer
from formset.widgets import DatePicker, DateTimePicker, DateTimeInput, Button
from formset.widgets import UploadedFileInput
# from django_starfield import Stars
from django_selectize import forms as s2forms
from formset.dialog import DialogModelForm
# from formset.fields import Activator
from formset.formfields.activator import Activator
from formset.renderers import ButtonVariant
from django_filters import FilterSet, ModelChoiceFilter
from formset.widgets import DecimalUnitInput
from formset.collection import AddSiblingActivator

from location_field.forms.plain import PlainLocationField

# class TextInfoField(Field):
#     input_type = "number"
#     template_name = "django/forms/widgets/info.html"

class RadioStarSelect(RadioSelect):
    template_name = "django/forms/widgets/radiostar.html"
    option_template_name = "django/forms/widgets/radio_star_option.html"


class SelectWidget(s2forms.SelectizeWidget):
    search_fields = [
        "title__icontains",
    ]


class mySelectize(Selectize):
    """
    Render widget suitable for TomSelect
    """
    template_name = '../foodster/templates/formset/default/widgets/myselectize.html'


class mySelect(ChoiceWidget):
    input_type = "select"
    template_name = "django/forms/widgets/myselect.html"
    option_template_name = "django/forms/widgets/select_option.html"
    add_id_index = False
    checked_attribute = {"selected": True}
    option_inherits_attrs = False

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.allow_multiple_selected:
            context["widget"]["attrs"]["multiple"] = True
        return context

    @staticmethod
    def _choice_has_empty_value(choice):
        """Return True if the choice's value is empty string or None."""
        value, _ = choice
        return value is None or value == ""

    def use_required_attribute(self, initial):
        """
        Don't render 'required' if the first <option> has a value, as that's
        invalid HTML.
        """
        use_required_attribute = super().use_required_attribute(initial)
        # 'required' is always okay for <select multiple>.
        if self.allow_multiple_selected:
            return use_required_attribute

        first_choice = next(iter(self.choices), None)
        return (
            use_required_attribute
            and first_choice is not None
            and self._choice_has_empty_value(first_choice)
        )


class mySelectType(mySelect):
    template_name = "django/forms/widgets/myselecttype.html"


class myTextarea(Widget):
    template_name = "django/forms/widgets/mytextarea.html"

    def __init__(self, attrs=None):
        # Use slightly better defaults than HTML's 20x2 box
        default_attrs = {"cols": "40", "rows": "10"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


# class dishTextarea(Widget):
#     template_name = "django/forms/widgets/textarea.html"
#
#     def __init__(self, attrs=None):
#         # Use slightly better defaults than HTML's 20x2 box
#         default_attrs = {"cols": "40", "rows": "10"}
#         if attrs:
#             default_attrs.update(attrs)
#         super().__init__(default_attrs)

class TextAreaWithMap(Textarea):
    template_name = "django/forms/widgets/textareawithmap.html"

    def __init__(self, attrs=None):
        # Use slightly better defaults than HTML's 20x2 box
        default_attrs = {"cols": "40", "rows": "10"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class CafeForm(ModelForm):

    class Meta:
      model = CafeModel
      fields = ['title','content','typeofkitchen','city','address','wwwaddress']
      labels = {'title': 'Название', 'content': 'Контент', 'typeofkitchen': 'Специфика заведения', 'address': 'Адрес',}

      widgets = {
            'title': Textarea(attrs={'rows': 1}),
            'content': Textarea(attrs={'rows': 2}),
            'typeofkitchen': Textarea(attrs={'rows': 1}),
            'address': TextAreaWithMap(attrs={'rows': 2}),
            # 'location': LocationWidget(based_fields=['address'],)
            # 'date_created': DateTimeInput(attrs={'hidden': 'true'}),
      }


class CafeImageForm(ModelForm):

    id = IntegerField(required=False, widget=HiddenInput)
    image = FileField(
        label="Фотография",
        widget=UploadedFileInput(
        #     attrs={
        #     'max-size': 1024 * 1024,
        # }
        )
    )

    class Meta:
      model = CafeImageModel
      fields = ['id', 'image']


class CafeImageCollection(FormCollection):
    min_siblings = 0
    induce_add_sibling = '.add_photos:active'
    image_form = CafeImageForm()
    related_field = 'cafe_fk'
    add_photos = AddSiblingActivator("Добавить фото")

    def get_or_create_instance(self, data):
        if data := data.get('image_form'):
            try:
                return self.instance.cafe_images.get(id=data.get('id') or 0), False
            except (AttributeError, CafeImageModel.DoesNotExist, ValueError):
                # return CafeImageModel(cafe_fk=self.instance)
                form = CafeImageForm(data=data)
                if form.is_valid():
                    return CafeImageModel(image=form.cleaned_data['image'], cafe_fk=self.instance), False
        return None, False

    # def retrieve_instance(self, data):
    #     if data := data.get('image_form'):
    #         try:
    #             return self.instance.cafe_images.get(id=data.get('id') or 0)
    #         except (AttributeError, CafeImageModel.DoesNotExist, ValueError):
    #             return CafeImageModel(cafe_fk=self.instance)


class CafeFormset(FormCollection):
    default_renderer = FormRenderer(field_css_classes='mb-3')
    cafe = CafeForm()
    cafe_images = CafeImageCollection()


class VisitForm(ModelForm):

    class Meta:

        model = VisitModel
        fields = ['data', 'description', 'register' ]
        labels = {'data': 'Дата посещения','description': 'Описание посещения','register':'Учитывать'}


        widgets = {
            'description': Textarea(attrs={'rows': 2}),
            'data': DateTimeInput,
            'average_dish_rating': HiddenInput,
        }

    # def construct_instance(self, main_object):
    #     # assert not self.partial
    #     #     rating = str(6-int(self.valid_holders['DishSet'].valid_holders['dish_form'].data['rating']))
    #         # self.valid_holders['DishSet'].valid_holders['dish_form'].data['rating'] = rating
    #     # main_object.rating = str(6 - int(main_object.rating))
    #     # self.cleaned_data['rating'] = str(6-int(self.cleaned_data['rating']))
    #     return construct_instance(self, main_object)



class DishLibraryForm(ModelForm):

    id = IntegerField(required=False, widget=HiddenInput)
    # queryset = DishLibraryModel.objects.filter(self,*args    )

    field_css_classes = 'row mb-3'
    label_css_classes = 'col-sm-3'
    control_css_classes = 'col-sm-9'

    class Meta:

        model = DishLibraryModel
        fields = ['id', 'name', 'dishcatalog_fk', 'type_of_kitchen_fk']
        labels = {'title': 'Название нового блюда заведения','dishcatalog_fk': 'Блюдо из справочника',}

        widgets = {
            'dishcatalog_fk': Selectize(search_lookup='title__icontains'),
        }

# class CafeFilterSet(FilterSet):
#     dish_fk = ModelChoiceFilter(
#         queryset=DishLibraryModel.objects.all(),
#     )
#
#     @property
#     def qs(self):
#         parent_qs = super().qs
#         if cafe := self.request.GET.get('filter-cafe'):
#             return parent_qs.filter(cafe_fk=cafe)
#         return parent_qs


class DishForm(ModelForm):

    id = IntegerField(required=False, widget=HiddenInput)
    currentuser = ModelChoiceField(required=False, queryset=CafeModel.objects.all() ,widget=HiddenInput)

    dish_info = IntegerField(required=False, widget=HiddenInput)

    cafe = ModelChoiceField(queryset=CafeModel.objects.all(),
        widget=Selectize(
            attrs={'disabled':'disabled'},
            placeholder="",
            ),
        # required=False,
        label="Кафе",
    )

    visit = ModelChoiceField(queryset=VisitModel.objects.all(),
                             widget=Selectize(attrs={'disabled': 'disabled'},
                                              placeholder="",
                                              ),
                             # required=False,
                             label="Визит",
    )

    add_dish = Activator(
        label="Добавить новое",
        widget=Button(
            action='activate',
            # button_variant=ButtonVariant.SECONDARY,
            attrs={'class': 'w-100 btn-outline-secondary',
                   'df-hide': '!DishSet.dish_form.currentuser',
                   'df-disable': 'DishSet.dish_form.dish_fk',
                   }
        ),
    )

    edit_dish = Activator(
        label="Редактировать",
        # required=False,
        widget=Button(
            action='activate(prefillPartial(DishSet.dish_form.dish_fk))',
            # button_variant=ButtonVariant.SECONDARY,
            attrs={
                'df-disable': '!DishSet.dish_form.dish_fk',
                'df-hide': '!DishSet.dish_form.currentuser',
                'class': 'w-100 btn-outline-secondary',
            }
        ),
    )

    price = fields.DecimalField(
        label="Цена",
        min_value=0,
        decimal_places=2,
        max_digits=10,
        step_size=1,  # allows multiples of 1 cent
    )


    def model_to_dict(self, main_object):
        rating = main_object.rating
        main_object.rating = str(6-int(rating))
        main_object.cafe = str(main_object.visit_fk.cafe_fk.id)
        return model_to_dict(main_object, fields=self._meta.fields, exclude=self._meta.exclude)

    class Meta:

        model = DishModel
        fields = ['id','currentuser','cafe','visit','dish_fk','dish_info','add_dish','edit_dish','description','price','rating',]
        labels = {'dish_fk': 'Название блюда этого заведения','description': 'Описание блюда', 'rating': 'Оценка блюда', 'price': 'Цена блюда' }

        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            'dish_fk': Selectize(
                attrs={'hx-get': '/dishinfo',
                       'hx-target':'[name="dish_info"]',
                       #id_edit_dish\\.CulinaryClassModel_fk_initial',
                       'hx-swap': 'outerHTML',
                       'hx-trigger':'click from:.dish_trigger delay:100ms, load, change changed',
                       },
                search_lookup='name__icontains',
                filter_by={'cafe': 'cafe_fk__id'},
                ),
            'rating': RadioStarSelect(attrs={'class': 'formset-inlined django-starfield'}, ),
            'price': DecimalUnitInput(prefix="€", suffix="руб.", fixed_decimal_places=True),

        }

class testform(ModelForm):


    class Meta:
        model = DishModel

        # fields = ['title','typeofdish_fk','dishcatalog_fk','description', 'rating','typeofdish_fk1','dishcatalog_fk1',]
        fields = '__all__'

        widgets = {
            'title': Textarea(attrs={'rows': 2}),
            'dish_fk': SelectWidget,
            'CulinaryClassModel_fk': SelectizeMultiple(search_lookup='name__icontains', max_items=15),

            # 'dishcatalog_fk1': Selectize(search_lookup='title__icontains'),
        }


class AddCulinaryClassForm(DialogModelForm):
    title = "Добавить новый класс в справочник"
    induce_open = '..add_dish.add_class:active || ..edit_dish.add_class:active'
    induce_close = '.changeclass:active || .cancelclass:active'

    class Meta:
        model = CulinaryClassModel
        fields = ['id','name',]


    id = IntegerField(
        widget=HiddenInput,
        required=False,
        help_text="Primary key of Reporter object. Leave empty to create a new object.",
    )

    cancelclass = Activator(
        label="Отмена",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='activate("clear")'),
    )
    changeclass = Activator(
        label="Сохранить",
        widget=Button(
            attrs={'class': 'w-40 mx-1'},
            button_variant=ButtonVariant.PRIMARY,
            # action='submitPartial -> activate("clear")',
            action='submitPartial -> setFieldValue(add_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id) -> setFieldValue(edit_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id) -> activate("clear")',
            # action='submitPartial -> setFieldValue(DishSet.edit_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> setFieldValue(add_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> activate("clear")',
        ),
    )

    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True

class EditCulinaryClassForm(DialogModelForm):
    title = "Изменить класс в справочнике"
    induce_open = '..edit_dish.edit_class:active || ..add_dish.edit_class:active'
    induce_close = '.changeclass:active || .cancelclass:active'

    class Meta:
        model = CulinaryClassModel
        fields = ['id','name',]


    id = IntegerField(
        widget=HiddenInput,
        required=False,
        help_text="Primary key of Reporter object. Leave empty to create a new object.",
    )

    cancelclass = Activator(
        label="Отмена",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='activate("clear")'),
    )
    changeclass = Activator(
        label="Сохранить",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            # action='submitPartial -> activate("clear")',
            action='submitPartial -> setFieldValue(edit_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id)  -> setFieldValue(add_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id)  -> activate("clear")',
            # action='submitPartial -> setFieldValue(DishSet.edit_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id) -> setFieldValue(add_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id) -> activate("clear")',
        ),
    )

    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True



class AddTypeForm(DialogModelForm):
    title = "Добавить новый тип в справочник"
    induce_open = '..add_dish.add_type:active || ..edit_dish.add_type:active'
    induce_close = '.changetype:active || .canceltype:active'

    class Meta:
        model = TypeOfKitchen
        fields = ['id','name',]


    id = IntegerField(
        widget=HiddenInput,
        required=False,
        help_text="Primary key of Reporter object. Leave empty to create a new object.",
    )

    canceltype = Activator(
        label="Отмена",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='activate("clear")'),
    )
    changetype = Activator(
        label="Сохранить",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='submitPartial -> setFieldValue(add_dish.type_of_kitchen_fk, ^type_of_kitchen_fk_id) ->  activate("clear")',
            # action='submitPartial -> setFieldValue(DishSet.edit_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> setFieldValue(add_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> activate("clear")',
        ),
    )

    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True

class EditTypeForm(DialogModelForm):
    title = "Изменить тип в справочнике"
    induce_open = '..edit_dish.edit_type:active || ..add_dish.edit_type:active'
    induce_close = '.changetype:active || .canceltype:active'

    class Meta:
        model = TypeOfKitchen
        fields = ['id','name',]


    id = IntegerField(
        widget=HiddenInput,
        required=False,
        help_text="Primary key of Reporter object. Leave empty to create a new object.",
    )

    canceltype = Activator(
        label="Отмена",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='activate("clear")'),
    )
    changetype = Activator(
        label="Сохранить",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='submitPartial -> setFieldValue(edit_dish.type_of_kitchen_fk, ^type_of_kitchen_fk_id) -> activate("clear")',
            # action='submitPartial -> setFieldValue(DishSet.edit_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id) -> setFieldValue(add_dish.CulinaryClassModel_fk, ^CulinaryClassModel_fk_id) -> activate("clear")',
        ),
    )

    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True





class AddDishCatalogForm(DialogModelForm):
    title = "Добавить блюдо в справочник"
    induce_open = '..add_dish.add_cat:active || ..edit_dish.add_cat:active'
    induce_close = '.changecat:active || .cancelcat:active'

    class Meta:
        model = DishCatalog
        fields = ['id','name',]


    # id = IntegerField(
    #     widget=HiddenInput,
    #     required=False,
    #     help_text="Primary key of Reporter object. Leave empty to create a new object.",
    # )

    cancelcat = Activator(
        label="Отмена",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='activate("clear")'),
    )
    changecat = Activator(
        label="Сохранить",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='submitPartial -> setFieldValue(edit_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> setFieldValue(add_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> activate("clear")',
        ),
    )

    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True

class EditDishCatalogForm(DialogModelForm):
    title = "Изменить блюдо в справочнике"
    induce_open = '..edit_dish.edit_cat:active || ..add_dish.edit_cat:active'
    induce_close = '.changecat:active || .cancelcat:active'

    class Meta:
        model = DishCatalog
        fields = ['id','name',]


    id = IntegerField(
        widget=HiddenInput,
        required=False,
        help_text="Primary key of Reporter object. Leave empty to create a new object.",
    )

    cancelcat = Activator(
        label="Отмена",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='activate("clear")'),
    )
    changecat = Activator(
        label="Сохранить",
        widget=Button(
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
            action='submitPartial -> setFieldValue(edit_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> setFieldValue(add_dish.dishcatalog_fk, ^dishcatalog_fk_id) -> activate("clear")',
        ),
    )

    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True



class ChangeDishLibraryForm(DialogModelForm):
    title = "Изменить блюдо этого заведения"
    induce_open = '..DishSet.dish_form.edit_dish:active'
    induce_close = '.change:active || .cancel:active'

    id = IntegerField(
        widget=HiddenInput,
        required=False,
        help_text="Primary key of Reporter object. Leave empty to create a new object.",
    )

    add_cat = Activator(
        label="Добавить новое",
        widget=Button(
            action='activate',
            # button_variant=ButtonVariant.PRIMARY,
            attrs={'class': 'w-40 mx-1 btn-outline-secondary ', }

        ),
    )

    edit_cat = Activator(
        label="Редактировать",
        widget=Button(
            action='activate(prefillPartial(edit_dish.dishcatalog_fk))',
            attrs={'class': 'w-40 mx-1 btn-outline-secondary',
                   'df-disable': '!edit_dish.dishcatalog_fk',
                   },
            # button_variant=ButtonVariant.PRIMARY,
        ),
    )

    add_class = Activator(
        label="Добавить новый",
        widget=Button(
            action='activate',
            # button_variant=ButtonVariant.PRIMARY,
            attrs={'class': 'w-40 mx-1 btn-outline-secondary ', }

        ),
    )

    edit_class = Activator(
        label="Редактировать",
        widget=Button(
            action='activate(prefillPartial(edit_dish.CulinaryClassModel_fk))',
            attrs={'class': 'w-40 mx-1 btn-outline-secondary',
                   'df-disable': '!edit_dish.CulinaryClassModel_fk',
                   },
            # button_variant=ButtonVariant.PRIMARY,
        ),
    )

    add_type = Activator(
        label="Добавить новый",
        widget=Button(
            action='activate',
            # button_variant=ButtonVariant.PRIMARY,
            attrs={'class': 'w-40 mx-1 btn-outline-secondary ', }

        ),
    )

    edit_type = Activator(
        label="Редактировать",
        widget=Button(
            action='activate(prefillPartial(edit_dish.type_of_kitchen_fk))',
            attrs={'class': 'w-40 mx-1 btn-outline-secondary',
                   'df-disable': '!edit_dish.type_of_kitchen_fk',
                   },
            # button_variant=ButtonVariant.PRIMARY,
        ),
    )


    cancel = Activator(
        label="Отмена",
        widget=Button(
            attrs={'class': 'w-100 mt-3', },
            button_variant=ButtonVariant.PRIMARY,
            action='activate("clear")'
    ),
    )
    change = Activator(
        label="Сохранить",
        widget=Button(
            attrs={'class': 'w-100 dish_trigger mt-1',
                   # 'hx-get': '/dishinfo', 'hx-target': '[name="dish_info"]', 'hx-swap': 'outerHTML', 'hx-include': 'dish_fk_id',
                   # 'hx-trigger': 'click',
                   },
            button_variant=ButtonVariant.PRIMARY,
            action='submitPartial -> setFieldValue(DishSet.dish_form.dish_fk, ^dish_fk_id) -> activate("clear")',
        ),
    )

    class Meta:
        model = DishLibraryModel
        fields = ['id', 'name' ,'dishcatalog_fk','add_cat','edit_cat','CulinaryClassModel_fk','add_class','edit_class','type_of_kitchen_fk','add_type','edit_type']
        # fields =['__all__', 'title', 'induce_open', 'induce_close', 'id', 'cancel', 'change']

        widgets = {
            'dishcatalog_fk': Selectize(search_lookup='name__icontains', placeholder=""),
            'CulinaryClassModel_fk': SelectizeMultiple(search_lookup='name__icontains', placeholder=""),
            'type_of_kitchen_fk': Selectize(search_lookup='name__icontains', placeholder=""),

        }


    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True


class AddDishLibraryForm(DialogModelForm):
    title = "Добавить новое блюдо для заведения"
    induce_open = '..DishSet.dish_form.add_dish:active'
    induce_close = '.change:active || .cancel:active'

    # id = IntegerField(
    #     widget=HiddenInput,
    #     required=False,
    #     help_text="Primary key of Reporter object. Leave empty to create a new object.",
    # )

    add_cat = Activator(
        label="Добавить новое",
        widget=Button(
            action='activate',
            # button_variant=ButtonVariant.PRIMARY,
            attrs={'class': 'w-40 mx-1 btn-outline-secondary', }

        ),
    )

    edit_cat = Activator(
        label="Редактировать",
        widget=Button(
            action='activate(prefillPartial(add_dish.dishcatalog_fk))',
            attrs={'class': 'w-40 mx-1 btn-outline-secondary',
                   'df-disable': '!add_dish.dishcatalog_fk',
                   },
            # button_variant=ButtonVariant.PRIMARY,
        ),
    )

    add_class = Activator(
        label="Добавить новый",
        widget=Button(
            action='activate',
            # button_variant=ButtonVariant.PRIMARY,
            attrs={'class': 'w-40 mx-1 btn-outline-secondary ', }

        ),
    )

    edit_class = Activator(
        label="Редактировать",
        widget=Button(
            action='activate(prefillPartial(add_dish.CulinaryClassModel_fk))',
            attrs={'class': 'w-40 mx-1 btn-outline-secondary',
                   'df-disable': '!add_dish.CulinaryClassModel_fk',
                   },
            # button_variant=ButtonVariant.PRIMARY,
        ),
    )

    add_type = Activator(
        label="Добавить новый",
        widget=Button(
            action='activate',
            # button_variant=ButtonVariant.PRIMARY,
            attrs={'class': 'w-40 mx-1 btn-outline-secondary ', }

        ),
    )

    edit_type = Activator(
        label="Редактировать",
        widget=Button(
            action='activate(prefillPartial(add_dish.CulinaryClassModel_fk))',
            attrs={'class': 'w-40 mx-1 btn-outline-secondary',
                   'df-disable': '!add_dish.type_of_kitchen_fk',
                   },
            # button_variant=ButtonVariant.PRIMARY,
        ),
    )

    cancel = Activator(
        label="Отмена",
        widget=Button(
            action='activate("clear")',
            attrs={'class': 'w-40 mx-1', },
            button_variant=ButtonVariant.PRIMARY,
        ),
    )
    change = Activator(
        label="Сохранить",
        widget=Button(
            action='submitPartial -> setFieldValue(DishSet.dish_form.dish_fk, ^dish_fk_id) -> activate("clear")',
            attrs={'class': 'w-40 mx-1 dish_trigger', },
            button_variant=ButtonVariant.PRIMARY,
        ),
    )

    class Meta:
        model = DishLibraryModel
        fields = ['name' ,'dishcatalog_fk','add_cat','edit_cat','CulinaryClassModel_fk','add_class','edit_class','type_of_kitchen_fk','add_type','edit_type']
        # fields =['__all__', 'title', 'induce_open', 'induce_close', 'id', 'cancel', 'change']

        widgets = {
            'dishcatalog_fk': Selectize(search_lookup='name__icontains'),
            'CulinaryClassModel_fk': SelectizeMultiple(search_lookup='name__icontains'),
            'type_of_kitchen_fk': Selectize(search_lookup='name__icontains'),

        }


    def is_valid(self):
        if self.partial:
            return super().is_valid()
        self._errors = {}
        return True


class DishImageForm(ModelForm):

    id = IntegerField(required=False, widget=HiddenInput)
    image = FileField(
        label="Фотография",
        widget=UploadedFileInput(
        #     attrs={
        #     'max-size': 1024 * 1024,
        # }
        )
    )

    class Meta:
      model = DishImageModel
      fields = ['id', 'image']


class DishImageCollection(FormCollection):
    min_siblings = 0
    induce_add_sibling = '.add_photos:active'

    # legend = 'Фотографии'
    image_form = DishImageForm()
    related_field = 'dish_fk'

    add_photos = AddSiblingActivator("Добавить фото")

    def get_or_create_instance(self, data):
        if data := data.get('image_form'):
            try:
                return self.instance.dish_images.get(id=data.get('id') or 0), False
            except (AttributeError, DishImageModel.DoesNotExist, ValueError):
                form = DishImageForm(data=data)
                if form.is_valid():
                    return DishImageModel(image=form.cleaned_data['image'], dish_fk=self.instance), False
        return None, False


class DishSet(FormCollection):
    dish_form = DishForm()
    dish_images = DishImageCollection()


class DishFormset(FormCollection):
    # add_label = 'Добавить новое блюдо'
    # legend = 'Блюда'

    default_renderer = FormRenderer(
        form_css_classes='row',
        field_css_classes={
            '*': 'mb-2 col-12 dj-required',
            'add_dish': 'mb-2 col-6 d-inline-block',
            'edit_dish': 'mb-2 col-6 d-inline-block',
            'add_cat': 'mb-2 col-6 d-inline-block',
            'edit_cat': 'mb-2 col-6 d-inline-block',
            'add_class': 'mb-2 col-6 d-inline-block',
            'edit_class': 'mb-2 col-6 d-inline-block',
            'add_type': 'mb-2 col-6 d-inline-block',
            'edit_type': 'mb-2 col-6 d-inline-block',
            'cancel': 'mb-2 col-4 d-inline-block',
            'change': 'mb-2 col-4 d-inline-block',
            'cancelcat': 'mb-2 col-6 d-inline-block',
            'changecat': 'mb-2 col-6 d-inline-block',

            # 'cafe':'mb-2 col-6 d-inline-block',
        })



    DishSet = DishSet()

    add_cat_form = AddDishCatalogForm(is_modal=True)
    edit_cat_form = EditDishCatalogForm(is_modal=True)

    edit_class_form = EditCulinaryClassForm(is_modal=True)
    add_class_form = AddCulinaryClassForm(is_modal=True)

    edit_type_form = EditTypeForm(is_modal=True)
    add_type_form = AddTypeForm(is_modal=True)

    add_dish = AddDishLibraryForm(is_modal=True)
    edit_dish = ChangeDishLibraryForm(is_modal=True)

    # def construct_instance(self, main_object):
    #     assert not self.partial
    #     instance = construct_instance(self.valid_holders['DishSet'], main_object)
    #     instance.save()
    #     return instance


class VisitImageForm(ModelForm):

    id = IntegerField(required=False, widget=HiddenInput)
    image = FileField(
        label="Фотография",
        widget=UploadedFileInput(
        #     attrs={
        #     'max-size': 1024 * 1024,
        # }
        )
    )

    class Meta:
      model = VisitImageModel
      fields = ['id', 'image']


class VisitImageCollection(FormCollection):
    min_siblings = 0
    induce_add_sibling = '.add_photos:active'
    image_form = VisitImageForm()
    related_field = 'visit_fk'

    add_photos = AddSiblingActivator("Добавить фото")

    def get_or_create_instance(self, data):
        if data := data.get('image_form'):
            try:
                return self.instance.visit_images.get(id=data.get('id') or 0), False
            except (AttributeError, VisitImageModel.DoesNotExist, ValueError):
                # return CafeImageModel(cafe_fk=self.instance)
                form = VisitImageForm(data=data)
                if form.is_valid():
                    return VisitImageModel(image=form.cleaned_data['image'], visit_fk=self.instance), False
        return None, False


    # def retrieve_instance(self, data):
    #     if data := data.get('image_form'):
    #         try:
    #             return self.instance.visit_images.get(id=data.get('id') or 0)
    #         except (AttributeError, VisitImageModel.DoesNotExist, ValueError):
    #             return VisitImageModel(visit_fk=self.instance)



class VisitFormset(FormCollection):
    # legend = 'Визит'
    default_renderer = FormRenderer(
        field_css_classes='row mb-3',
        label_css_classes='col-sm-3',
        control_css_classes='col-sm-9',
    )

    default_renderer = FormRenderer(field_css_classes='mb-3')
    visit = VisitForm()
    visit_images = VisitImageCollection()

    # visit_dishes = DishFormCollection()
    # issue = ChangeDishLibraryForm()


