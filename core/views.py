from django.db.models import Count, Avg
from django.views.generic import UpdateView, FormView, TemplateView
from django.forms.models import construct_instance
# from formset.collection import construct_instance
from formset.views import FormViewMixin, IncompleteSelectResponseMixin
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from .models import CafeModel, VisitModel, DishModel, CafeImageModel, TypeOfDishes, DishCatalog, DishLibraryModel, \
    TypeOfKitchen, CulinaryClassModel, DishImageModel, VisitImageModel, IntroImageModel
from .forms import CafeFormset, VisitFormset, CafeImageForm, DishForm, VisitForm, CafeForm, testform, DishLibraryForm, DishFormset
from formset.views import FormCollectionView, EditCollectionView, FormViewMixin, FormView
from django.http.response import JsonResponse, HttpResponseBadRequest
from .tables import DishesTable, CafesTable, VisitsTable, MyVisitsTable, TypeTable, ClassTable, BestDishesTable, VisitsListTable
from .filters import DishLibraryFilterSet, CafesLibraryFilterSet, VisitsFilterSet, MyVisitsFilterSet, DishesFilterSet, KitchenTypeFilterSet, ClassFilterSet, BestDishesFilterSet
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.files import File
from decimal import Decimal
from django.http import HttpResponse


def process_initial(data):
    """
    Рекурсивно обрабатывает данные initial, чтобы сделать их JSON-совместимыми.
    """
    if isinstance(data, dict):
        return {
            key: process_initial(value) for key, value in data.items()
        }
    elif isinstance(data, list):
        return [process_initial(item) for item in data]
    elif isinstance(data, File):
        return data.url if data else None
    else:
        return data

# def dishinfo(request):
#     context = {}
#     dish_fk_id = request.GET.get('dish_fk')
#     if dish_fk_id:
#         dish = DishLibraryModel.objects.get(pk=dish_fk_id)
#         context['dish'] = DishLibraryModel.objects.get(pk=dish_fk_id)
#         context['classes'] = list(dish.CulinaryClassModel_fk.values_list('name', flat=True))
#         return render(request, 'dish_info.html', context)
#     return "<br>"

# def dishinfo(request):
#     dish_fk_id = request.GET.get('dish_fk')
#     if not dish_fk_id:
#         return HttpResponse('<input type="hidden" name="dish_info" form="id_DishSet.dish_form" id="id_DishSet.dish_form.dish_info">', content_type='text/html')
#
#     try:
#         dish = DishLibraryModel.objects.get(pk=dish_fk_id)
#         return render(request, 'dish_info.html', {'dish': dish,'classes': list(dish.CulinaryClassModel_fk.values_list('name', flat=True))})
#     except DishLibraryModel.DoesNotExist:
#         return HttpResponse('', content_type='text/html')


def dishinfo(request):
    dish_fk_id = request.GET.get('dish_fk')
    if not dish_fk_id:
        # Возвращаем пустое скрытое поле
        return HttpResponse(
            '<input type="hidden" name="dish_info" form="id_DishSet.dish_form" id="id_DishSet.dish_form.dish_info">',
            content_type='text/html'
        )

    try:
        dish = DishLibraryModel.objects.get(pk=dish_fk_id)
        # Получаем ID классов как int
        classes_ids = list(dish.CulinaryClassModel_fk.values_list('pk', flat=True))
    except DishLibraryModel.DoesNotExist:
        # Возвращаем пустой ответ
        return HttpResponse('', content_type='text/html')

    # Рендерим шаблон dish_info.html
    info_html = render(request, 'dish_info.html', {
        'dish': dish,
        'classes': list(dish.CulinaryClassModel_fk.values_list('name', flat=True))
    }).content.decode('utf-8')

    # # Создаём script с initial
    # initial_html = f'''
    # <script id="id_edit_dish.CulinaryClassModel_fk_initial" type="application/json">
    #     {classes_ids}
    # </script>
    # '''

    # Объединяем и возвращаем
    # return HttpResponse(info_html + initial_html, content_type='text/html')
    return HttpResponse(info_html, content_type='text/html')
# def iommitest(request):
#
#     response = EditTable(auto__model=CulinaryClassModel, columns__name__field__include=True,)
#     # response =  crud_views(model=CulinaryClassModel)
#     return response

class StartView(TemplateView):
    template_name = "start.html"

    # def get_context_data(self, *args, **kwargs):
    #     context = self.get_context_data(self, *args, **kwargs)
    #
    #     context['images'] = IntroImageModel.objects.all()
    #     return context

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = IntroImageModel.objects.all()
        return context

class TypeEditTableView(TemplateView):
    template_name = "django_tables2/type_row.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['record'] = kwargs.get('pk')
        item = TypeOfKitchen.objects.get(id=kwargs.get('pk'))
        context['name'] = item.name
        return self.render_to_response(context)


class ClassEditTableView(TemplateView):
    template_name = "django_tables2/class_row.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['record'] = kwargs.get('pk')
        item = CulinaryClassModel.objects.get(id=kwargs.get('pk'))
        context['name'] = item.name
        return self.render_to_response(context)


class DictView(TemplateView):
    template_name = "dicts/dicts.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        types_count = TypeOfKitchen.objects.count()
        class_count = CulinaryClassModel.objects.count()
        dishes_count = DishModel.objects.count()
        context['types_count'] = types_count
        context['class_count'] = class_count
        context['dishes_count'] = dishes_count

        return self.render_to_response(context)


class ClassDictListView(LoginRequiredMixin, SingleTableMixin, FilterView):

    model = CulinaryClassModel
    table_class = ClassTable
    queryset = model.objects.all()
    filterset_class = ClassFilterSet
    paginate_by = 12

    def get_template_names(self):
        if self.request.htmx:
            template_name = "dicts/class_dict_list_htmx.html"
        else:
            template_name = "dicts/class_dict_list.html"

        return template_name


class ClassDictUpdateListView(TemplateView):
    template_name = "dicts/class_dict_list_htmx.html"

    def get(self, request, *args, **kwargs):

        item = CulinaryClassModel.objects.get(pk=kwargs.get('cpk'))
        if item.name != request.GET.get('name'):
            item.name = request.GET.get('name')
            item.save()

        return redirect('core:classes')


class TypeDictListView(LoginRequiredMixin, SingleTableMixin, FilterView):

    model = TypeOfKitchen
    table_class = TypeTable
    queryset = model.objects.all()
    filterset_class = KitchenTypeFilterSet
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            template_name = "dicts/type_dict_list_htmx.html"
        else:
            template_name = "dicts/type_dict_list.html"

        return template_name


class TypeDictUpdateListView(TemplateView):
    template_name = "dicts/type_dict_list_htmx.html"

    def get(self, request, *args, **kwargs):

        item = TypeOfKitchen.objects.get(pk=kwargs.get('tpk'))
        if item.name != request.GET.get('name'):
            item.name = request.GET.get('name')
            item.save()

        return redirect('core:types')


# class TypeOfKitchenAutocomplete(Select2QuerySetView):
#
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#
#         if self.q:
#             qs = TypeOfKitchen.objects.all()
#             qs = qs.filter(title__istartswith=self.q)
#             return qs
#
#         return TypeOfKitchen.objects.all()[:2]
#
#
# class DishAutocomplete(autocomplete.Select2QuerySetView):
#
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#
#         if self.q:
#             qs = DishCatalog.objects.all()
#             qs = qs.filter(title__istartswith=self.q)
#             return qs
#
#         return DishCatalog.objects.all()[:2]


class DishView(CreateView):
    form_class = DishForm
    model = DishModel

    template_name = "test_dishview.html"


class CafeFormsetView(EditCollectionView):

        model = CafeModel
        collection_class = CafeFormset
        template_name = "add_cafe_formset.html"


        extra_context = {
            'click_actions': 'disable -> submit -> reload !~ scrollToError',
            'force_submission': False,
        }

        def get_object(self, queryset=None):

            pk = self.kwargs.get(self.pk_url_kwarg)
            slug = self.kwargs.get(self.slug_url_kwarg)
            if pk is None and slug is None:
                return self.model()
            return super().get_object()


        def get_success_url(self):
            return self.request.META.get('HTTP_REFERER')


def edit_dish(request,id,idv,idd):
    context = {}
    cafe = CafeModel.objects.get(id=id)
    visit_id = VisitModel.objects.get(id=idv)
    edited_dish = DishModel.objects.get(id=idd)

    if request.method == 'GET':
        form = DishForm(instance=edited_dish)
        context = {'cafe': cafe, 'visit': visit_id, 'dish': edited_dish,'visitform': form}
        return render(request, 'editdishform.html', context)

    if request.method == 'POST':
        context = {}
        form = DishForm(request.POST, instance=edited_dish)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.cafe = cafe
            obj.visit = visit_id
            obj.save()

        dishes = DishModel.objects.filter(cafe=id, visit=idv)
        context = {'cafe': cafe, 'visit': visit_id, 'dishes': dishes, 'visitform': form}
        return render(request, 'dishes_list.html', context)


def add_dish(request,id,idv):

    if request.method == 'GET':
        context = {}
        cafe = CafeModel.objects.get(id=id)
        visit_id = VisitModel.objects.get(id=idv)

        form = DishForm()
        context = {'cafe': cafe, 'visit': visit_id, 'visitform': form}
        return render(request, 'dishform.html', context)

    if request.method == 'POST':
        context = {}
        form = DishForm(request.POST)
        visit_id = VisitModel.objects.get(id=idv)

        # id = form.cafe
        cafe = CafeModel.objects.get(id=id)
        # form.instance.cafe = cafe

        if form.is_valid():
            obj = form.save(commit=False)
            obj.cafe = cafe
            obj.visit = visit_id
            obj.save()


            dishes = DishModel.objects.filter(cafe=id, visit=idv)
            form = DishForm()
            # dishes = dish.objects.all()
            context = {'dishes': dishes, 'cafe': cafe, 'visit': visit_id, 'visitform': form}

            return render(request, 'dishes_list.html', context)


def dishes_list(request):
    context = {}
    # dishes = dish.objects.filter(cafe=cafe)


    # cafes = Cafe.objects.all()
    # if query:
    #     allcafe = cafes.filter(title__icontains=query)
    # else:
    #     # allcafe = []
    #     allcafe = cafes
    dishes = DishModel.objects.all()


    context = {'dishes': dishes}
    return render(request, 'dishes_list.html', context)





class TestView(IncompleteSelectResponseMixin, FormViewMixin, UpdateView):
    model = DishModel
    form_class = testform
    template_name = "testform.html"

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset
    #
    # def get_object(self, queryset=None):
    #     if queryset is None:
    #         queryset = self.get_queryset()
    #     return queryset.last()

    # def get_object(self, queryset=None):
    #     pk = self.kwargs.get(self.pk_url_kwarg)
    #     slug = self.kwargs.get(self.slug_url_kwarg)
    #     cafe_id = CafeModel.objects.get(pk=self.kwargs.get('cafe_id'))
    #     queryset = DishCatalog.objects.all()
    #
    #     if pk is None and slug is None:
    #         return self.model(cafe_fk=cafe_id)
    #     return super().get_object()


class TestViewCollection(EditCollectionView):
    model = DishModel
    collection_class = DishFormset
    template_name = "testform.html"

class VisitView(EditCollectionView):
    model = VisitModel
    collection_class = VisitFormset
    template_name = "add_visit_formset.html"
    # success_url = '/cafes/<int:cafe_id>/cab/'

    extra_context = {
        'click_actions': 'disable -> submit -> reload !~ scrollToError',
        'force_submission': False,
    }

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        cafe_id = CafeModel.objects.get(pk=self.kwargs.get('cafe_id'))

        if pk is None and slug is None:
            return self.model(cafe_fk=cafe_id)
        return super().get_object()

    # def form_collection_valid(self, form_collection):
    #     if form_collection.is_valid():
    #         rating_j=0
    #         counter= form_collection.cleaned_data.get('visit_dishes').__len__()
    #         for j in form_collection.cleaned_data.get('visit_dishes'):
    #             rating_j = rating_j + 6-int(j.get('dish_form').get('rating'))
    #         average_rating = rating_j / counter
    #         form_collection.cleaned_data['visit']['average_dish_rating'] = average_rating
    #         return super().form_collection_valid(form_collection)
    #     else:
    #         return self.form_collection_invalid(form_collection)


    def get_success_url(self):
    #     return self.request.META.get('HTTP_REFERER')
        return '/cafe/'+str(self.kwargs.get('cafe_id'))


class add_dish_library(FormViewMixin, UpdateView):
    default_renderer = 'bootstrap'
    model = DishLibraryModel
    form_class = DishLibraryForm
    template_name = 'add_dish.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['dish_fk'] = self.request.GET.get('dish_fk')
        context_data['myval'] = self.request.GET.get('myval')
        if self.object.pk is None:
            context_data['add'] = True
        else:
            context_data['change'] = True
        return context_data


    def get_object(self, queryset=None):
        if self.request.GET:
            # items = self.request.GET.keys()
            # key =''
            # for item in items:
            #     key = item;
            pk = self.request.GET.get('dish_fk')
            myval = self.request.GET.get('myval')

            if pk:
                # return super().get_object()
                return DishLibraryModel.objects.get(pk=pk)
            else:
                return self.model()
        else:
            pk = self.kwargs.get(self.pk_url_kwarg)
            slug = self.kwargs.get(self.slug_url_kwarg)
            # id = DishLibraryModel.objects.get(pk=self.kwargs.get('id'))
            # pk = self.request.GET.get('dish_fk')

            if pk is None:
                form_data = self.get_form_kwargs()
                if form_data['data'].get('id'):
                    pk = form_data['data'].get('id')

            if pk is None and slug is None:
                return self.model()
            else:
                return DishLibraryModel.objects.get(pk=pk)
            return super().get_object()


def get_dish_id(request):
    print(request)
    title = request.GET.get('title')
    myval = request.GET.get('myVal')
    dish_fk = request.GET.get('dish_fk')

    dish = DishLibraryModel.objects.filter(title=title)[:1]
    print(dish[0].title)
    if not myval:
        myval = dish[0].id

    # response = HttpResponse(headers={"title": title, "id_myval": myval})
    context = {'title': dish[0].title, 'myval': myval, 'dish_fk': dish_fk}

    return render(request, 'get_dish_id.html', context)


def add_visit(request, cafe_id):
    context = {}
    cafe = CafeModel.objects.get(id=cafe_id)
    form = VisitForm()
    context = {'form': form, 'cafe': cafe}
    if request.method == 'GET':
        return render(request, 'add_visit.html', context)

    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.cafe = cafe
            obj.save()
            visits = VisitModel.objects.filter(cafe=cafe)
            context = {'visits': visits, 'cafe': cafe}
            return render(request, 'visits.html', context)
    # return render(request, 'cafecab.html', context)


def add_new_visit(request, id):
    context = {}
    cafe = CafeModel.objects.get(id=id)
    form = VisitForm()
    # form = AddVisit(initial={'cafe': id},instance=cafe)
    # form[cafe].value()
    context = {'form': form, 'cafe': cafe}
    if request.method == 'GET':
        return render(request, 'add_new_visit.html', context)

    if request.method == 'POST':
        form = VisitForm(request.POST)
        # form.instance.cafe = cafe
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            # return redirect('/search/')
        return redirect("/cafes/" + str(id) + "/cab/")
    # return render(request, 'cafecab.html', context)


def add_new_cafe(request):
    context = {}
    form = CafeForm()
    context = {'form': form,}
    if request.method == 'GET':
        return render(request, 'add_new_cafe.html', context)

    if request.method == 'POST':
        form = CafeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return redirect('/search/')
        # return render(request, 'add_new_cafe.html', context)


def display_cafes(request):
    context = {}
    Cafes = CafeModel.objects.all()
    form = CafeForm()
    context = {'form': form, 'Cafes': Cafes}

    return render(request, 'display_cafes.html', context)


def visit_cafe(request, id, idv):
    context = {}
    cafe = CafeModel.objects.get(id=id)
    thisvisit = VisitModel.objects.get(id=idv)
    visitform = DishForm()
    dishes = DishModel.objects.filter(cafe = id, visit_fk = idv)

    context = {'cafe': cafe,'visitform': visitform, 'visit_fk':thisvisit, 'dishes': dishes }

    return render(request, 'visit_cab.html', context)


def cab_cafe(request, cafe_id):

    if request.META.get('HTTP_HX_REQUEST'):
        if request.method == "PATCH":
            return redirect()

        context = {}
        cafe = CafeModel.objects.get(id=cafe_id)
        cafesvisits = VisitModel.objects.filter(cafe_fk=cafe).order_by('-data')[:10]
        form = CafeForm(instance=cafe)
        visitform = VisitForm(instance=cafe)
        context = {'form': form, 'cafe': cafe, 'visitform': visitform, 'visits': cafesvisits}

        if request.method == 'POST':
            form = CafeForm(request.POST, instance=cafe)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                return redirect('/search/')

        return render(request, 'cafecab_htmx.html', context)

    else:
        # myback = request.META['HTTP_REFERER']

        # if request.method == "PATCH":
        #     return redirect(myback)

        context = {}
        cafe = CafeModel.objects.get(id=cafe_id)
        cafesvisits = VisitModel.objects.filter(cafe_fk=cafe).order_by('-data')[:10]
        form = CafeForm(instance=cafe)
        visitform = VisitForm(instance=cafe)
        context = {'form': form,'cafe': cafe,'visitform': visitform, 'visits':cafesvisits}

        if request.method == 'POST':
            form = CafeForm(request.POST, instance=cafe)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.save()
                return redirect('/search/')

        return render(request, 'cafecab.html', context)


def search_results_view(request):
    query = request.GET.get('search', '')
    print(f'{query = }')

    cafes = CafeModel.objects.all()

    if query:
        allcafe = cafes.filter(title__icontains=query).order_by("-date_created")
    else:
        # allcafe = []
        allcafe = cafes.order_by("-date_created")

    context = {'allcafe': allcafe, 'count': cafes.count()}
    return render(request, 'search_results.html', context)


def sort_cafe(request):

    sortlist = {'title': 'по названию', 'date_created': 'по дате создания', 'visits_count': 'по количеству посещений'}

    if request.META.get('HTTP_HX_REQUEST'):

        sortdef = sortlist.get(request.GET.get('myVal1'))
        sortstr = request.GET.get('myVal1')

        updown = sortlist.get(request.GET.get('myVal2'))
        updownstr = request.GET.get('myVal2')

        bisortdown = 'bi-sort-up'

        if request.GET.get('myVal3') == 'sort':
            if updownstr == "+":
                updownstr = '-'
                bisortdown = 'bi-sort-up'
                # bisortdown = 'bi-caret-down'
            else:
                updownstr = '+'
                bisortdown = 'bi-sort-down-alt'
                # bisortdown = 'bi-caret-up'
    else:
        updownstr = '+'
        sortdef = 'по дате создания'
        sortstr = 'date_created'

    if updownstr == '-':
        orderedsortstr = updownstr+sortstr
    else:
        orderedsortstr = sortstr


    allcafe = CafeModel.objects.all().order_by(orderedsortstr)
    context = {'allcafe': allcafe, 'count': allcafe.count(), 'sortlist': sortlist, 'sortdef': sortdef, 'sortstr': sortstr, 'updown': updown, 'updownstr': updownstr,  'bisortdown': bisortdown }

    return render(request, 'search.html', context)


def search_cafe(request):
    context = {}
    sortdef = 'по дате создания'
    sortstr = 'date_created'
    # sortdef = 'date_created'
    sortlist = {'title': 'по названию', 'date_created': 'по дате создания', 'visits_count': 'по количеству посещений'}
    updown = "+"
    updownstr = "+"
    allcafe = CafeModel.objects.all().order_by("date_created")
    bisortdown = 'bi-sort-down-alt'
    context = {'allcafe': allcafe, 'count': allcafe.count(), 'sortlist': sortlist, 'sortstr': sortstr,'sortdef': sortdef, 'updown': updown, 'updownstr': updownstr, 'bisortdown': bisortdown }

    return render(request, 'search_cafes.html', context)


# @require_http_methods(['DELETE'])
def delete_cafe(request, id):
    CafeModel.objects.filter(id=id).delete()
    Cafes = CafeModel.objects.all()
    return render(request, 'cafes_list.html', {'Cafes': Cafes})

# def add_cafe(request):
#     context = {}
#     # myback = request.META['HTTP_REFERER']
#     # if request.method == 'PATCH':
#     #     return redirect(myback)
#     #
#     # if request.method == 'GET':
#     #    form = add_cafe()
#     #    context = {'form':form}
#     #    return render(request,'add_cafe.html',context)
#     #
#     # if request.method == 'POST':
#     #    form = AddCafe(request.POST)
#     #    if form.is_valid():
#     #        form.save()
#     #    if request.htmx:
#     #        return redirect('display_cafes')
#
#     if request.method == 'POST':
#        form = AddCafe(request.POST)
#        if form.is_valid():
#            form.save()
#        if request.htmx:
#            Cafes = Cafe.objects.all()
#            form = AddCafe()
#            context = {'form': form, 'Cafes': Cafes}
#            return render(request, 'display_cafes.html', context)

def dishes_search_results_view(request, id):
    query = request.GET.get('dish_fk', '')
    print(f'{query = }')

    # if request.htmx:
    #     # txt = request.htmx.trigger.split('.')[0],request.htmx.trigger.split('.')[1],request.htmx.trigger.split('.')[2],'typeofdish_fk'
    #     txt = request.htmx.trigger.split('.')
    #     txt[3] = "typeofdish_fk"
    #     id_dish_input = '.'.join(txt).strip()
    #     number_of_form = txt[1]

    # types_of_dish = TypeOfDishes.objects.all()

    # dish_list=''
    selected_dishes = ''
    # # selected_dish=""
    Dishes = DishLibraryModel.objects.all()
    #
    if query:
        selected_dishes = Dishes.filter(title__icontains=query)

    # try:
    #     selected_dish = DishModel.objects.get(dish_fk=query)
    # except:
    # selected_dish = ""
    #
    # if selected_dish:
    #     cat_dish_selected = selected_dish.dishcatalog_fk
    #     dish_list = DishCatalog.objects.all().filter(type_fk_id=selected_dish.typeofdish_fk_id)
    # else:
    #     cat_dish_selected = "------"
    #
    context = {'selected_dishes': selected_dishes,
    #            # 'id_dish_input': id_dish_input,
    #            # 'number_of_form': number_of_form,
    #            # 'types_of_dish': types_of_dish,
    #            'selected_dish': selected_dish,
    #            'dish_list': dish_list,
    #            'cat_dish_selected': cat_dish_selected,
               }
    #
    #
    return render(request, 'dish_search_result.html', context)


def dish_type_filter(request, id):
    query = request.GET.get('title', '')

    (f'{query = }')
    id_type_dish = request.htmx.request.GET.get('typeofdish_fk')
    target_id = request.htmx.target
    dish_list = DishCatalog.objects.all().filter(type_fk_id=id_type_dish)

    context = {'dish_list': dish_list,
               'target_id': target_id,
    }

    return render(request, 'dish_type_filter.html', context)


# class test_iommi(Page):
#     create_form = Form.create(auto__model=DishLibraryModel)
#     a_table = Table(auto__model=DishLibraryModel,
#
#                     columns__edit=Column.edit(
#                         after=0,
#                     ),
#                     columns__delete=Column.delete(
#                     ),
#
#
#                     )
#
#     class Meta:
#         title = 'Список блюд'


class add_dish_lib(FormViewMixin, UpdateView):
    default_renderer = 'bootstrap'
    model = DishLibraryModel
    form_class = DishLibraryForm
    template_name = 'add_dish.html'


    # def get_object(self, queryset=None):
    #     pk = self.kwargs.get(self.pk_url_kwarg)
    #     slug = self.kwargs.get(self.slug_url_kwarg)
    #     # cafe_id = CafeModel.objects.get(pk=self.kwargs.get('cafe_id'))
    #
    #     return super().get_object()


class TableView(SingleTableMixin, FilterView):
    model = DishLibraryModel
    table_class = DishesTable
    queryset = model.objects.all()
    filterset_class = DishLibraryFilterSet
    paginate_by = 10

    # template_name = 'table.html'
    # if self.request.htmx:
    #     template_name = 'table.html'
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     self.filterset = DishLibraryFilterSet(self.request.GET, queryset)
    #     return self.filterset.qs
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['filterset'] = self.filterset
    #     context['filter'] = DishLibraryFilterSet(self.request.GET, queryset=self.get_queryset())
    #     return context

    def get_template_names(self):
        if self.request.htmx:
            template_name = "table_htmx.html"
        else:
            template_name = "table.html"

        return template_name


class CafesListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    model = CafeModel
    table_class = CafesTable
    queryset = model.objects.all()
    filterset_class = CafesLibraryFilterSet
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            template_name = "cafeslist_htmx.html"
        else:
            template_name = "cafeslist.html"

        return template_name


class VisitsView(SingleTableMixin, FilterView):
    model = VisitModel
    table_class = VisitsTable
    # queryset = model.objects.all()
    paginate_by = 10
    template_name = "visits_list.html"
    filterset_class = VisitsFilterSet

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cafe_id'] = self.kwargs.get('pk')
        context['cafe'] = CafeModel.objects.get(id=self.kwargs.get('pk'))
        return context


    def get_queryset(self):
        model = VisitModel
        cafe = CafeModel.objects.get(id=self.kwargs.get('pk'))
        queryset = model.objects.filter(cafe_fk=cafe)
        return queryset


class Cafe_cab(EditCollectionView):
    model = CafeModel
    collection_class = CafeFormset
    template_name = "cafe_cab.html"
    # success_url = "/cafes/"

    extra_context = {
        'click_actions': 'disable -> submit -> reload !~ scrollToError',
        'force_submission': False,
    }

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is None and slug is None:
            return self.model()
        return super().get_object()

    def get_context_data(self, *args, **kwargs):
        context = super(EditCollectionView, self).get_context_data(*args, **kwargs)
        if 'pk' in self.kwargs:
            context['images'] = CafeImageModel.objects.filter(cafe_fk=self.kwargs['pk'])

        context['way'] = self.request.GET.get("way")

        if not self.request.user.is_authenticated:
            context['form_collection'].initial.pop('cafe_images')
        else:
            if not self.request.user.is_staff:
                context['form_collection'].initial.pop('cafe_images')
        return context


    def get_success_url(self):
        # return self.request.META.get('HTTP_REFERER')
        return "/cafe/" + str(self.kwargs.get('pk')) + "/?way=list"

class VisitCab(EditCollectionView):
    model = VisitModel
    collection_class = VisitFormset
    template_name = "visitcab.html"
    success_url = "/cafes/"

    def get_context_data(self, *args, **kwargs):
        context = super(EditCollectionView, self).get_context_data(*args, **kwargs)
        context['way'] = self.request.GET.get("way")
        context['cafe_fk'] = self.kwargs.get('cpk')
        if 'pk' in self.kwargs:
            context['images'] = VisitImageModel.objects.filter(visit_fk=self.kwargs['pk'])

        if not self.request.user.is_authenticated:
            context['form_collection'].initial.pop('visit_images')
        else:
            if not self.request.user.is_staff:
                context['form_collection'].initial.pop('visit_images')
        return context


    def get_success_url(self):
        # return "/cafe/"+str(VisitModel.objects.get(pk=self.kwargs.get('cpk')).cafe_fk.id)+"/"+str(VisitModel.objects.get(pk=self.kwargs.get('cpk')).id)+"/?way = list"
        # return reverse('core:cafe_cab', kwargs={'pk': self.kwargs.get('cpk')})
        return "/cafe/"+str(self.kwargs.get('cpk'))+"/"+str(self.kwargs.get('pk'))+"/?way=list"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        # pk = self.kwargs.get("vpk")
        cafe_fk = CafeModel.objects.get(pk=self.kwargs.get('cpk'))

        if pk is None and slug is None:
            return self.model(cafe_fk=cafe_fk, user=self.request.user)
        return super().get_object()

    # def form_collection_valid(self, form_collection):
    #     if form_collection.is_valid():
    #         rating_j=0
    #         counter = 0
    #         # counter= form_collection.cleaned_data.get('visit_dishes').__len__()
    #         for j in form_collection.cleaned_data.get('visit_dishes'):
    #             counter += 1
    #             rating_j = rating_j + 6-int(j.get('dish_form').get('rating'))
    #         average_rating = rating_j / counter
    #         form_collection.cleaned_data['visit']['average_dish_rating'] = average_rating
    #         return super().form_collection_valid(form_collection)
    #     else:
    #         return self.form_collection_invalid(form_collection)

    def form_collection_valid(self, form_collection):
        if not form_collection.is_valid():
            return self.form_collection_invalid(form_collection)
        else:
            # print(form_collection.valid_holders)
            # if not form_collection.valid_holders.get('visit').data.get('register'):
            #     cafe = self.object.cafe_fk
            #     visits = VisitModel.objects.filter(cafe_fk=cafe)

            # cafe_fk = CafeModel.objects.get(pk=self.kwargs.get('cpk'))
    #     form_collection.valid_holders['visit'].data['user'] = self.request.user
    #     form_collection.valid_holders['visit'].data['cafe_fk'] = cafe_fk
    #     form_collection.valid_holders['visit'].cleaned_data['user'] = self.request.user
    #     form_collection.valid_holders['visit'].cleaned_data['cafe_fk'] = cafe_fk
    #
            return super().form_collection_valid(form_collection)

    # def form_valid(self, form):
    #     if extra_data := self.get_extra_data():
    #         if extra_data.get('add') is True:
    #             cafe_fk = CafeModel.objects.get(pk=self.kwargs.get('cpk'))
    #             form.instance.cafe_fk = cafe_fk
    #             form.instance.user = self.request.user
    #             form.instance.save()
    #     return super().form_valid(form)


class DishesListView(SingleTableMixin, FilterView):
    model = DishModel
    table_class = DishesTable
    # queryset = model.objects.all()
    filterset_class = DishesFilterSet
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            template_name = "disheslist_htmx.html"
        else:
            template_name = "disheslist.html"

        return template_name

    def get_queryset(self):
        model = DishModel
        visit = VisitModel.objects.get(id=self.kwargs.get('vpk'))
        queryset = model.objects.filter(visit_fk=visit)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visit_id'] = self.kwargs.get('vpk')
        return context


class add_new_dish(FormViewMixin, UpdateView):
    model = DishModel
    form_class = DishForm
    template_name = "add_new_dish.html"
    success_url = "/cafes/"


    # def get_object(self, queryset=None):
    #     pk = self.kwargs.get(self.pk_url_kwarg)
    #     slug = self.kwargs.get(self.slug_url_kwarg)
    #     visit_fk_id = VisitModel.objects.get(pk=self.kwargs.get('visit_fk'))
    #
    #     if pk is None and slug is None:
    #         return self.model(visit_fk=visit_fk_id)
    #     return super().get_object()
    #
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['cafe'] = CafesTable
        context['visit_fk'] = self.kwargs.get('vpk')
        return context
    #
    def get_success_url(self):
        return "/cafe/"+str(VisitModel.objects.get(pk=self.kwargs.get('vpk')).cafe_fk.id)+"/"+str(VisitModel.objects.get(pk=self.kwargs.get('vpk')).id)+"/"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        # visit_fk_id = VisitModel.objects.get(pk=self.kwargs.get('visit_fk'))

        if pk is None and slug is None:
            return self.model()
        return super().get_object()


    def form_valid(self, form):
        if extra_data := self.get_extra_data():
            if extra_data.get('add') is True:
                visit_fk = VisitModel.objects.get(pk=self.kwargs.get('vpk'))
                form.instance.visit_fk = visit_fk
                form.instance.save()
            if extra_data.get('delete') is True:
                form.instance.delete()
                return JsonResponse({'success_url': self.get_success_url()})
        return super().form_valid(form)

def serialize_value(value):
    """
    Рекурсивная функция для конвертации неподдерживаемых типов
    """
    if isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [serialize_value(item) for item in value]
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, File):
        return value.url if value else None
    elif isinstance(value, (str, int, float, bool)) or value is None:
        return value
    else:
        return str(value)  # резервный вариант

class BestDishesListView(SingleTableMixin, FilterView):
    model = DishModel
    table_class = BestDishesTable
    # queryset = model.objects.values_list('dish_fk', flat=True).distinct()
    # queryset = model.objects.values('dish_fk').annotate(group_count = Count('pk'))
    queryset = model.objects.values('dish_fk','dish_fk__name','visit_fk__cafe_fk','visit_fk__cafe_fk','visit_fk__cafe_fk__title').annotate(group_count=Count('pk'), group_average=Avg('rating')).order_by('-group_average')
    # queryset = model.objects.all().distinct('pk')
    paginate_by = 10
    filterset_class = BestDishesFilterSet

    def get_template_names(self):
        if self.request.htmx:
            template_name = "bestdisheslist_htmx.html"
        else:
            template_name = "bestdisheslist.html"

        return template_name


class MyVisitsListView(SingleTableMixin, FilterView):
    model = VisitModel
    table_class = MyVisitsTable
    filterset_class = MyVisitsFilterSet

    def get_queryset(self):
        queryset = VisitModel.objects.filter(user=self.request.user)
        return queryset


    def get_template_names(self):
        if self.request.htmx:
            template_name = "my_visits_list_htmx.html"
        else:
            template_name = "my_visits_list.html"

        return template_name


class add_new_dish_collection(EditCollectionView):
    model = DishModel
    collection_class = DishFormset
    template_name = "add_new_dish_collection.html"

    def _fetch_partial_data(self):
        collection_class = self.get_collection_class()
        empty_holder = collection_class
        initial = self.get_initial()
        bucket = None

        for part in self.request.GET['path'].split('.'):
            if not (empty_holder := getattr(empty_holder, 'declared_holders', {}).get(part)):
                break
            bucket = initial.setdefault(part, {})

        if bucket is not None:
            try:
                instance = empty_holder._meta.model.objects.get(pk=self.request.GET.get('pk'))
                data = type(empty_holder)(instance=instance).initial

                # 🔧 Модификация: преобразуем ManyToMany поля в список ID
                # Пример: для edit_dish
                if self.request.GET['path'] == 'edit_dish':
                    if hasattr(instance, 'CulinaryClassModel_fk'):
                        data['CulinaryClassModel_fk'] = list(
                            instance.CulinaryClassModel_fk.values_list('pk', flat=True)
                        )
                    # Добавь другие ManyToMany поля при необходимости
                    # if hasattr(instance, 'type_of_kitchen_fk'):
                    #     data['type_of_kitchen_fk'] = instance.type_of_kitchen_fk.pk

                cleaned_data = serialize_value(data)
                bucket.update(**cleaned_data)
            except empty_holder._meta.model.DoesNotExist:
                pass
            else:
                return JsonResponse(serialize_value(initial))

        return HttpResponseBadRequest("Invalid path value")

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        visit_id = VisitModel.objects.get(pk=self.kwargs.get('vpk'))

        if pk is None and slug is None:
            return self.model(visit_fk=visit_id,user=self.request.user)
        return super().get_object()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visit_fk'] = self.kwargs.get('vpk')
        context['visit'] = context['dishmodel'].visit_fk
        # context['cafe'] = context['dishmodel'].visit_fk.cafe_fk
        context['form_collection'].declared_holders['DishSet'].declared_holders['dish_form'].fields['cafe'].initial = context['dishmodel'].visit_fk.cafe_fk.id
        if 'pk' in self.kwargs:
            context['images'] = DishImageModel.objects.filter(dish_fk=self.kwargs['pk'])

        # qr = context['form_collection'].declared_holders['dish_form'].fields['cafe'].queryset
        # qr = qr.filter(id=context['dishmodel'].visit_fk.cafe_fk.id)
        # context['form_collection'].declared_holders['dish_form'].fields['cafe'].queryset = qr
        context['form_collection'].declared_holders['DishSet'].declared_holders['dish_form'].fields['visit'].initial = context['dishmodel'].visit_fk.id
        context['form_collection'].declared_holders['DishSet'].declared_holders['dish_form'].fields['currentuser'].initial = self.request.user.id

        if 'pk' in self.kwargs:
            dish = DishLibraryModel.objects.get(pk=context['dishmodel'].dish_fk.pk)
            classes = dish.CulinaryClassModel_fk.values_list('pk', flat=True)
            context['form_collection'].declared_holders['edit_dish'].fields['CulinaryClassModel_fk'].initial = classes

        if not self.request.user.is_authenticated:
            context['form_collection'].initial['DishSet'].pop('dish_images')
        else:
            if not (context['visit'].user==self.request.user) or not (self.request.user.is_superuser):
                context['form_collection'].initial['DishSet'].pop('dish_images')
        return context

    def get_success_url(self):
        return "/cafe/"+str(VisitModel.objects.get(pk=self.kwargs.get('vpk')).cafe_fk.id)+"/"+str(VisitModel.objects.get(pk=self.kwargs.get('vpk')).id)+"/?way=list"

    def form_collection_valid(self, form_collection):
        if form_collection.partial:
            if form_collection.valid_holders.get('edit_type_form'):
                if not (valid_holder := form_collection.valid_holders.get('edit_type_form')):
                    return HttpResponseBadRequest("Form data is missing.")
                if id := valid_holder.cleaned_data['id']:
                    type_model_item = TypeOfKitchen.objects.get(id=id)
                    construct_instance(valid_holder, type_model_item)
                else:
                    type_model_item = construct_instance(valid_holder, TypeOfKitchen())
                type_model_item.save()
                return JsonResponse({'type_of_kitchen_fk_id': type_model_item.id})
            elif form_collection.valid_holders.get('add_type_form'):
                if not (valid_holder := form_collection.valid_holders.get('add_type_form')):
                    return HttpResponseBadRequest("Form data is missing.")
                type_model_item = construct_instance(valid_holder, TypeOfKitchen())
                type_model_item.save()
                return JsonResponse({'type_of_kitchen_fk_id': type_model_item.id})

            elif form_collection.valid_holders.get('edit_cat_form'):
                if not (valid_holder := form_collection.valid_holders.get('edit_cat_form')):
                    return HttpResponseBadRequest("Form data is missing.")
                if id := valid_holder.cleaned_data['id']:
                    cat_model_item = DishCatalog.objects.get(id=id)
                    construct_instance(valid_holder, cat_model_item)
                else:
                    cat_model_item = construct_instance(valid_holder, DishCatalog())
                cat_model_item.save()
                return JsonResponse({'dishcatalog_fk_id': cat_model_item.id})
            elif form_collection.valid_holders.get('add_cat_form'):
                if not (valid_holder := form_collection.valid_holders.get('add_cat_form')):
                    return HttpResponseBadRequest("Form data is missing.")
                cat_model_item = construct_instance(valid_holder, DishCatalog())
                cat_model_item.save()
                return JsonResponse({'dishcatalog_fk_id': cat_model_item.id})
            elif form_collection.valid_holders.get('add_class_form'):
                if not (valid_holder := form_collection.valid_holders.get('add_class_form')):
                    return HttpResponseBadRequest("Form data is missing.")
                # if id := valid_holder.cleaned_data['id']:
                #     class_model_item = CulinaryClassModel.objects.get(id=id)
                #     construct_instance(valid_holder, class_model_item)
                # else:
                class_model_item = construct_instance(valid_holder, CulinaryClassModel())
                class_model_item.save()
                return JsonResponse({'CulinaryClassModel_fk_id': class_model_item.id})
            elif form_collection.valid_holders.get('edit_class_form'):
                if not (valid_holder := form_collection.valid_holders.get('edit_class_form')):
                    return HttpResponseBadRequest("Form data is missing.")
                if id := valid_holder.cleaned_data['id']:
                    class_model_item = CulinaryClassModel.objects.get(id=id)
                    construct_instance(valid_holder, class_model_item)
                else:
                    class_model_item = construct_instance(valid_holder, CulinaryClassModel())
                class_model_item.save()
                return JsonResponse({'CulinaryClassModel_fk_id': class_model_item.id})
            elif form_collection.valid_holders.get('add_dish'):
                if not (valid_holder := form_collection.valid_holders.get('add_dish')):
                    if not (valid_holder := form_collection.valid_holders.get('add_dish')):
                        return HttpResponseBadRequest("Form data is missing.")
                if id := valid_holder.cleaned_data.get('id'):
                    DishLibraryModelItem = DishLibraryModel.objects.get(id=id)
                    construct_instance(valid_holder, DishLibraryModelItem)
                else:
                    DishLibraryModelItem = construct_instance(valid_holder, DishLibraryModel())

                visit_id = VisitModel.objects.get(pk=self.kwargs.get('vpk'))
                DishLibraryModelItem.cafe_fk = CafeModel.objects.get(pk=visit_id.cafe_fk.id)
                DishLibraryModelItem.save()
                DishLibraryModelItem.CulinaryClassModel_fk.set(form_collection.cleaned_data['add_dish']['CulinaryClassModel_fk'])
                # return JsonResponse({'dish_fk_id': form_collection.cleaned_data['add_dish']['CulinaryClassModel_fk']})
                return JsonResponse({'dish_fk_id': DishLibraryModelItem.id})
            elif form_collection.valid_holders.get('edit_dish'):
                if not (valid_holder := form_collection.valid_holders.get('edit_dish')):
                    if not (valid_holder := form_collection.valid_holders.get('edit_dish')):
                        return HttpResponseBadRequest("Form data is missing.")
                if id := valid_holder.cleaned_data.get('id'):
                    DishLibraryModelItem = DishLibraryModel.objects.get(id=id)
                    construct_instance(valid_holder, DishLibraryModelItem)
                else:
                    DishLibraryModelItem = construct_instance(valid_holder, DishLibraryModel())
                if self.kwargs.get('cpk'):
                    cafe = CafeModel.objects.get(pk=self.kwargs.get('cpk'))
                else:
                    cafe = VisitModel.objects.get(pk=self.kwargs.get('vpk')).cafe_fk
                DishLibraryModelItem.cafe_fk = cafe
                DishLibraryModelItem.save()
                DishLibraryModelItem.CulinaryClassModel_fk.set(form_collection.cleaned_data['edit_dish']['CulinaryClassModel_fk'])
                # form_collection.cleaned_data['edit_dish']['CulinaryClassModel_fk']
                return JsonResponse({'dish_fk_id': DishLibraryModelItem.id})

        # rating = str(6 - int(form_collection.instance.rating))
        # form_collection.data['DishSet']['dish_form']['rating'] = rating
        # form_collection.initial['DishSet']['dish_form']['rating'] = rating
        # form_collection.instance.rating = rating
        form_collection.valid_holders['DishSet'].cleaned_data.get('dish_form')['rating'] = str(6 - int(form_collection.valid_holders['DishSet'].cleaned_data.get('dish_form')['rating']))
        return super().form_collection_valid(form_collection)

class VisitsList(SingleTableMixin, FilterView):
    model = VisitModel
    table_class = VisitsListTable

    def get_queryset(self):
        # queryset = VisitModel.objects.filter(visit_dishes__id=self.kwargs.get('pk')).distinct()
        queryset = VisitModel.objects.filter(visit_dishes__dish_fk__id=self.kwargs.get('pk'))

        return queryset

    def get_template_names(self):
        if self.request.htmx:
            template_name = "dish_visits_list_htmx.html"
        else:
            template_name = "dish_visits_list.html"

        return template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class DishPhotosList(TemplateView):
    model = DishImageModel
    template_name = "dishesphotoslist.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = DishImageModel.objects.filter(dish_fk__dish_fk=self.kwargs['pk'])
        return context