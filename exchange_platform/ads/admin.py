from django.contrib import admin

from .models import (
    Ad,
    ExchangeProposal,
    Category,
)

'''
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'type', 'category', 'creation_date', 'update_date',
    list_display_links = 'pk', 'title', 'type', 'category',
    ordering = 'pk', 'title', 'type', 'category',
    search_fields = 'title', 'type', 'category',


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name',
    list_display_links = 'pk', 'name',
    ordering = 'pk', 'name',
    search_fields = 'name',
'''


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'get_short_description', 'user', 'category', 'condition', 'created_at'
    list_display_links = 'pk', 'title', 'user', 'category',
    ordering = 'pk', 'title', 'category', 'condition', 'created_at'
    search_fields = 'title', 'category', 'user', 'condition', 'description'

    def get_short_description(self, obj: Ad):
        return f'{obj.description[:20]}...'

    get_short_description.short_description = 'Короткое описание'


@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = 'pk', 'get_ad_sender_title', 'get_ad_receiver_title', 'get_short_comment', 'status', 'created_at',
    list_display_links = 'pk', 'get_ad_sender_title', 'get_ad_receiver_title', 'status',
    ordering = 'pk', 'created_at',
    search_fields = 'ad_sender__title', 'ad_receiver__title', 'get_short_comment', 'status',

    def get_ad_sender_title(self, obj: ExchangeProposal):
        return obj.ad_sender.title

    get_ad_sender_title.short_description = 'Заголовок отправленного предложения'

    def get_ad_receiver_title(self, obj: ExchangeProposal):
        return obj.ad_receiver.title

    get_ad_receiver_title.short_description = 'Заголовок полученного предложения'

    def get_short_comment(self, obj: ExchangeProposal):
        return f'{obj.comment[:20]}...'

    get_short_comment.short_description = 'Короткий комментарий '


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'category_name',
    list_display_links = 'pk', 'category_name',
    ordering = 'pk', 'category_name',
    search_fields = 'category_name',
