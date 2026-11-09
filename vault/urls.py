from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('upload/', views.upload_document, name='upload_document'),
    path('download/<int:document_id>/', views.download_document, name='download_document'),
    path('delete/<int:document_id>/', views.delete_document, name='delete_document'),
    path('about/', views.about, name='about'),
    path('help/', views.help_page, name='help')
]