from django.urls import path
from . import views 

urlpatterns = [
    path('',views.index,name="index"),
    path('delete-transaction/<id>/', views.delete_transaction , name="delete_transaction"),
    path('update_transaction/<id>/',views.update_transaction , name="update_transaction")
]
  