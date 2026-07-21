from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('main/', views.main_view, name='main'),
    path('logout/', views.logout_view, name='logout'),
    path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('auth/kakao/', views.kakao_login, name='kakao_login'),
    path('auth/kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('auth/naver/', views.naver_login, name='naver_login'),
    path('auth/naver/callback/', views.naver_callback, name='naver_callback'),
]
