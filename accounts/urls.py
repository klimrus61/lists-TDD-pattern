from django.urls import path
from accounts import views
from django.contrib.auth.views import logout_then_login


urlpatterns = [
    path('send_login_email/', views.send_login_email, name='send_login_email'),
    path('login/', views.login, name='login'),
    path('logout/', logout_then_login, name='logout')
]
