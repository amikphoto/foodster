from django.contrib import admin
from .models import CafeModel, CafeImageModel, VisitModel, DishModel, TypeOfDishes, DishCatalog, DishLibraryModel, TypeOfKitchen, CulinaryClassModel
# Register your models here.

admin.site.register(VisitModel)
admin.site.register(DishModel)
admin.site.register(CafeImageModel)
admin.site.register(TypeOfDishes)
admin.site.register(DishCatalog)
admin.site.register(DishLibraryModel)
admin.site.register(TypeOfKitchen)
admin.site.register(CulinaryClassModel)

class GalleryInLine(admin.TabularInline):
    fk_name = 'cafe_fk'
    model = CafeImageModel


@admin.register(CafeModel)
class CafeAdmin(admin.ModelAdmin):
    inlines = [GalleryInLine,]
