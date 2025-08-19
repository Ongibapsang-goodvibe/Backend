from django.urls import path
from .views import *


app_name = "accounts"

urlpatterns = [
    # path('login/', login, name='login'),
    path('<int:pk>/disease/', DiseaseUpdateView.as_view()),
    path('user/', UserView.as_view(), name="user-info")
]