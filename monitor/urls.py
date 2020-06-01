from django.urls import path
from monitor.views import (
    MySQLConnectorView, update_mysql_connector, copy_mysql_connector,
    MongoConnectorView, update_mongo_connector, copy_mongo_connector
)

urlpatterns = [
    path('', MySQLConnectorView.as_view()),
    path('connectors/', MySQLConnectorView.as_view()),
    path('connectors/c/<int:index>/', copy_mysql_connector),
    path('connectors/e/<int:index>/', update_mysql_connector),
    path('mongo-connectors/', MongoConnectorView.as_view()),
    path('mongo-connectors/c/<int:index>/', copy_mongo_connector),
    path('mongo-connectors/e/<int:index>/', update_mongo_connector),
]
