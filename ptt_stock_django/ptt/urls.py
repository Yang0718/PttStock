from django.urls import path
from . import  views
urlpatterns = [
    path('', views.home, name='home'), # 引號裡面留白是因為這邊在做首頁。
                                       # views.home的home指的是views.py裡面的function。
    path('db.html', views.db, name='db'),
    path('about.html', views.about, name='about'),
]