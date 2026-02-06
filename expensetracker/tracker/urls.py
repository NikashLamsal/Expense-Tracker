from django.urls import path
from . import views 

urlpatterns = [
    path('',views.index,name="index"),
    path('delete-transaction/<id>/', views.delete_transaction , name="delete_transaction"),
    path('update_transaction/<id>/',views.update_transaction , name="update_transaction"),
    path('login/', views.login_view,name="login_page"),
    path('register/', views.register_view,name="register_page"),
    path('logout/',views.logout_view,name = "logout_page"),
]