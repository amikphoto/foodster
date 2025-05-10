from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_resized import ResizedImageField
from django.contrib.contenttypes.fields import GenericRelation
# from rating.models import Rating

# Create your models here.
class TypeOfDishes(models.Model):
    title = models.CharField(max_length=200,)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Type_of_dishes"


class DishCatalog(models.Model):
    name = models.CharField(max_length=200,)
    # type_fk = models.ForeignKey(TypeOfDishes, on_delete=models.CASCADE, null=True, related_name='type_dishes',)

    class Meta:
        verbose_name_plural = "DishesCatalog"

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<{self.__class__.__name__}: "{self.name}">'




class CafeModel(models.Model):

    title = models.CharField(verbose_name="Название", max_length=200)
    content = models.TextField(verbose_name="Описание")
    typeofkitchen = models.TextField(verbose_name="Специфика заведения")
    address = models.TextField(verbose_name="Адрес")
    average_rating = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Рейтинг")

    date_created = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name_plural = "Cafes"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/cafe/{self.pk}/'

class CafeImageModel(models.Model):

    title = models.CharField(max_length=200, default='')
    # image = models.ImageField(upload_to='media')
    image = ResizedImageField(upload_to='media/cafes/%Y.%m.%d')
    cafe_fk = models.ForeignKey(CafeModel, on_delete=models.CASCADE, related_name='cafe_images',)

    def __str__(self):
        return self.title


class VisitModel(models.Model):

    data = models.DateTimeField(default=timezone.now, verbose_name="Дата визита")
    cafe_fk = models.ForeignKey(CafeModel, on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Описание визита")
    average_dish_rating = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Рейтинг блюд визита")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    register = models.BooleanField(default=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name_plural = "Visits"

    def get_absolute_url(self):
        if self.cafe_fk:
            return self.cafe_fk.get_absolute_url()+str(self.pk)+"/"
        return '#none'


class VisitImageModel(models.Model):

    title = models.CharField(max_length=200, default='')
    # image = models.ImageField(upload_to='media')
    image = ResizedImageField(upload_to='media/visits/%Y.%m.%d')
    visit_fk = models.ForeignKey(VisitModel, on_delete=models.CASCADE, related_name='visit_images',)

    def __str__(self):
        return self.title


class CulinaryClassModel(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return 'none'



class TypeOfKitchen(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class DishLibraryModel(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name='Наименование')
    dishcatalog_fk = models.ForeignKey(DishCatalog, on_delete=models.CASCADE, verbose_name='Блюдо-образец для сравнения', null=True, blank=True)
    type_of_kitchen_fk = models.ForeignKey(TypeOfKitchen, on_delete=models.CASCADE, verbose_name='Тип кухни')
    cafe_fk = models.ForeignKey(CafeModel, on_delete=models.CASCADE, verbose_name='', null=True, blank=True)
    CulinaryClassModel_fk = models.ForeignKey(CulinaryClassModel, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Кулинарный класс')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "LibraryDishes"

    def get_absolute_url(self):
        return f'/dishes/{self.pk}/'


class DishModel(models.Model):

    dish_fk = models.ForeignKey(DishLibraryModel,on_delete=models.CASCADE, related_name='bestdishes',)
    visit_fk = models.ForeignKey(VisitModel, on_delete=models.CASCADE, related_name='visit_dishes')
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    TYPE_SELECT = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        # ('6', '6'),
        # ('7', '7'),
    )
    rating=models.CharField(max_length=11,choices=TYPE_SELECT,default='0')
    rating2 = models.CharField(max_length=11, choices=TYPE_SELECT, default='0')

    def __str__(self):

        return self.dish_fk.name

    class Meta:
        verbose_name_plural = "Dishes"

    def get_absolute_url(self):
        return self.visit_fk.get_absolute_url()+str(self.pk)+"/"



class DishImageModel(models.Model):

    title = models.CharField(max_length=200, default='')
    # image = models.ImageField(upload_to='media')
    image = ResizedImageField(upload_to='media/dishes/%Y.%m.%d')
    dish_fk = models.ForeignKey(DishModel, on_delete=models.CASCADE, related_name='dish_images',)

    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    show_register_button = models.BooleanField(
        default=True,
        verbose_name="Показывать кнопку регистрации"
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def save(self, *args, **kwargs):
        # Оставляем только одну запись настроек
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj