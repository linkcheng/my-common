from django.urls import path
from common.views import CommonView

urlpatterns = [
    path('date/', CommonView.as_view()),
    path('date/<int:index>/', CommonView.as_view()),
    path('mobileAttribution/', CommonView.as_view()),
    path('mobileAttribution/<int:index>/', CommonView.as_view()),
    path('idAttribution/', CommonView.as_view()),
    path('idAttribution/<int:index>/', CommonView.as_view()),
]
