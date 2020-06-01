import logging
from django.contrib import admin

from monitor.models import Database, MySQLConnector, Mongo, MongoConnector

logger = logging.getLogger(__name__)


class MySQLAdmin(admin.ModelAdmin):
    fields = ('name', 'host', 'port', 'username', 'password')
    list_display = ('name', 'host', 'port', 'username')
    list_display_links = ('name', )

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj:
            obj.password = '******'
        return obj


class MySQLConnectorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('', {
            'fields': ('name', 'connector_class', 'tasks_max',)
        }),
        ('kafka配置', {
            'fields': ('history_kafka_topic', 'history_kafka_servers',)
        }),
        ('数据库配置', {
            'fields': ('database', 'server_id', 'server_name',)
        }),
        ('库过滤器配置', {
            'fields': ('schema_whitelist', 'schema_blacklist',)
        }),
        ('表过滤器配置', {
            'fields': ('table_whitelist', 'table_blacklist',)
        }),
        ('其他', {
            'fields': ('include_schema_changes',)
        }),
    )
    list_display = ('name', 'tasks_max', 'database', 'server_id', 'server_name')
    list_display_links = ('name',)


class MongoDBAdmin(admin.ModelAdmin):
    fields = ('name', 'host', 'username', 'password')
    list_display = ('name', 'host', 'username')
    list_display_links = ('name', )

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj:
            obj.password = '******'
        return obj


class MongoConnectorAdmin(admin.ModelAdmin):
    fieldsets = (
        ('', {
            'fields': ('name', 'connector_class', 'tasks_max',)
        }),
        ('数据库配置', {
            'fields': ('database', 'server_name',)
        }),
        ('库过滤器配置', {
            'fields': ('database_whitelist', 'database_blacklist',)
        }),
        ('集合过滤器配置', {
            'fields': ('collection_whitelist', 'collection_blacklist',)
        }),
    )
    list_display = ('name', 'tasks_max', 'database', 'server_name')
    list_display_links = ('name',)


admin.site.register(Database, MySQLAdmin)
admin.site.register(MySQLConnector, MySQLConnectorAdmin)
admin.site.register(Mongo, MongoDBAdmin)
admin.site.register(MongoConnector, MongoConnectorAdmin)

