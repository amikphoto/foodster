# core/cms_plugins.py
from cms.plugin_base import CMSPluginBase
from django.utils.safestring import mark_safe
from django.forms import Media
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _
from taggit.models import TaggedItem

from core.forms import TagSelectorForm
from core.models import TagSelector, CafeModel, DishModel, TypeOfKitchen, DishCatalog


class TagSelectorPlugin(CMSPluginBase):
    """Плагин для выбора тегов из существующих"""
    module = _('Blog')
    name = _('Tag Selector')
    model = TagSelector
    form = TagSelectorForm
    render_template = 'cms/plugins/tag_selector.html'
    cache = False

    # core/cms_plugins.py
    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        selected_tags = instance.tags.all()

        # Получаем все связанные объекты одним запросом
        from django.contrib.contenttypes.models import ContentType

        cafe_content_type = ContentType.objects.get_for_model(CafeModel)
        dish_content_type = ContentType.objects.get_for_model(DishModel)

        # Получаем все связи для выбранных тегов
        tagged_items = TaggedItem.objects.filter(
            tag__in=selected_tags
        ).select_related('content_type', 'tag')

        # Группируем по типам
        cafe_tags = []
        dish_tags = []
        category_tags = []

        for item in tagged_items:
            tag = item.tag
            obj = item.content_object

            if isinstance(obj, CafeModel):
                cafe_tags.append({
                    'tag': tag,
                    'object': obj,
                    'url': obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else None,
                })

            if isinstance(obj, DishCatalog):
                dish_tags.append({
                    'tag': tag,
                    'object': obj,
                    'url': obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else None,
                })

            if isinstance(obj, TypeOfKitchen):
                category_tags.append({
                    'tag': tag,
                    'object': obj,
                    'url': obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else None,
                })


        context.update({
            'selected_tags': selected_tags,
            'cafe_tags': cafe_tags,
            'dish_tags': dish_tags,
            'category_tags': category_tags,
            # 'tag_type_filter': instance.tag_type_filter,
            # 'show_count': instance.show_count,
            # 'limit': instance.limit,
        })

        return context

plugin_pool.register_plugin(TagSelectorPlugin)