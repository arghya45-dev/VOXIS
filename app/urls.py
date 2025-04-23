from django.urls import path  
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('/', views.home, name='home'),
    path("login/", views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),  # Added '/' for consistency
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
   
    path('assist/', views.assist, name='assist'),            # Home page → index.html
    path('ask-groq/', views.ask_groq, name='ask'),  # POST endpoint

    path('text_to_speech/', views.text_to_speech, name='text_to_speech'),
]