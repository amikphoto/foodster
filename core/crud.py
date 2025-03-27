from crudbuilder.abstract import BaseCrudBuilder
from core.models import CulinaryClassModel, DishLibraryModel

class ClassCrud(BaseCrudBuilder):
        model = CulinaryClassModel
        search_fields = ['name']
        tables2_fields = ('name',)
        tables2_css_class = "table table-bordered table-condensed"
        tables2_pagination = 20  # default is 10
        modelform_excludes = ['created_by', 'updated_by']
        login_required=False
        permission_required=False
        # permissions = {
        #   'list': 'example.person_list',
        #       'create': 'example.person_create'
        # }


class DishLibraryModelCrud(BaseCrudBuilder):
        model = DishLibraryModel
        # search_fields = ['name']
        tables2_fields = ('name','dishcatalog_fk','type_of_kitchen_fk')
        tables2_css_class = "table table-bordered table-condensed"
        tables2_pagination = 20  # default is 10
        # modelform_excludes = ['created_by', 'updated_by']
        login_required=False
        permission_required=False
        # permissions = {
        #   'list': 'example.person_list',
        #       'create': 'example.person_create'
        # }