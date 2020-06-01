import logging
from django.contrib import admin

from metadata.models import DatabaseConfig, SchemaConfig

logger = logging.getLogger(__name__)


class DatabaseConfigAdmin(admin.ModelAdmin):
    fields = ('name', 'host', 'port', 'username', 'password')
    list_display = ('name', 'host', 'port', 'username')
    list_display_links = ('name', )

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj:
            obj.password = '******'
        return obj


class SchemaConfigAdmin(admin.ModelAdmin):
    fields = ('database', 'schema_name')
    list_display = fields


admin.site.register(DatabaseConfig, DatabaseConfigAdmin)
admin.site.register(SchemaConfig, SchemaConfigAdmin)

