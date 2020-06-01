from django.urls import path
from user.views import (
    UserInfo,
    UserPwd,
    UserMenu,
    user_operation_log,
    UserLogin,
    user_logout,
)

urlpatterns = [
    path('', UserInfo.as_view()),
    path('info/', UserInfo.as_view()),
    path('pwd/', UserPwd.as_view()),

    path('menu/', UserMenu.as_view()),
    path('menu/<int:index>/', UserMenu.as_view()),

    path('log/', user_operation_log),
    path('log/<int:index>/', user_operation_log),

    path('login/', UserLogin.as_view(), name="login"),
    path('logout/', user_logout, name="logout"),
]
