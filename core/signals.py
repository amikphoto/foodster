from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import DishModel, VisitModel, CafeModel, TypeOfKitchen, DishCatalog
from unidecode import unidecode
from django.utils.text import slugify

from taggit.models import Tag

@receiver(post_save, sender=TypeOfKitchen)
def sync_type_tag(sender, instance, created, **kwargs):
        if instance.name:
                # Добавляем тег через TaggableManager (автоматически создает связь)
                instance.tags.add(instance.name)

                tag = Tag.objects.get(name=instance.name)
                transliterated_name = unidecode(instance.name)
                tag.slug = slugify(transliterated_name)
                tag.save()


@receiver(post_save, sender=DishCatalog)
def sync_dish_tag(sender, instance, created, **kwargs):
        print(instance)
        if instance.name:
                # Добавляем тег через TaggableManager (автоматически создает связь)
                instance.tags.add(instance.name)

                tag = Tag.objects.get(name=instance.name)
                transliterated_name = unidecode(instance.name)
                tag.slug = slugify(transliterated_name)
                tag.save()


@receiver(post_save, sender=CafeModel)
def sync_cafe_tag(sender, instance, created, **kwargs):
        if instance.title:
                # Добавляем тег через TaggableManager (автоматически создает связь)
                instance.tags.add(instance.title)

                tag = Tag.objects.get(name=instance.title)
                transliterated_name = unidecode(instance.title)
                tag.slug = slugify(transliterated_name)
                tag.save()

@receiver(post_save, sender=DishModel)
def raiting_dish_update(sender, created ,instance, **kwargs):
        # print(instance)
        cafe = instance.visit_fk.cafe_fk

        # if instance.visit_fk.register:
        visit = instance.visit_fk

        average_rating = 0
        count = 0
        # dishes = DishModel.objects.filter(visit_fk__cafe_fk=cafe)
        dishes = DishModel.objects.filter(visit_fk=visit)
        for dish in dishes:
                count += 1
                average_rating = average_rating + float(dish.rating)

        average_rating = average_rating / count
        visit.average_dish_rating = average_rating
        visit.save(update_fields=['average_dish_rating'])

        count = 0
        average_rating = 0
        visits = VisitModel.objects.filter(cafe_fk=cafe)
        for visit_item in visits:
                if not visit_item.register:
                        continue

                if visit_item.average_dish_rating:
                        count += 1
                        average_rating = average_rating + float(visit_item.average_dish_rating)

        if count == 0:
                average_rating = 0
        else:
                average_rating = average_rating / count

        cafe.average_rating = average_rating
        cafe.save()

@receiver(post_save, sender=VisitModel)
def raiting_visit_update(sender, created, instance, **kwargs):
        if not kwargs['update_fields']:
                count = 0
                average_rating = 0
                cafe = instance.cafe_fk
                visits = VisitModel.objects.filter(cafe_fk=cafe)
                for visit_item in visits:
                        if visit_item.register:
                                if visit_item.average_dish_rating:
                                        count += 1
                                        average_rating = average_rating + float(visit_item.average_dish_rating)

                if count != 0:
                        average_rating = average_rating / count
                else:
                        average_rating = 0

                cafe.average_rating = average_rating
                cafe.save()
