from django.contrib import admin

from . import models


# Change admin site header and title
admin.site.site_header = 'Placeholder Header'
admin.site.site_title = 'Placeholder Title'
admin.site.index_title = 'Placeholder Title'

@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['key', 'creator', 'published']
    list_filter = ['creator', 'published']
    search_fields = ['key', 'creator', 'published']
