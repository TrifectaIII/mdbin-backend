from django.contrib import admin

from .models import Document


# Change admin site header and title
admin.site.site_header = 'mdbin Admin Panel'
admin.site.site_title = 'mdbin Admin Panel'
admin.site.index_title = 'Home'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = ['keyHex', 'creator', 'published']
    list_filter = ['creator', 'published']
    search_fields = ['keyHex', 'creator']
    ordering = ['-published']
