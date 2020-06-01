from django.urls import path
from metadata.views import SearchView, DetailView, CommentView,GetDB

urlpatterns = [
    path('', SearchView.as_view()),
    path('databases/', GetDB.as_view()),
    path('search/', SearchView.as_view()),
    path('result/', SearchView.as_view()),
    path('detail/<table_schema>/<table_name>', DetailView.as_view()),
    path('comment/', CommentView.as_view()),
]
