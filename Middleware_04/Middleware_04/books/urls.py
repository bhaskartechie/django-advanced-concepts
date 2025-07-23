from django.urls import path
from .views import book_list, book_detail, add_review

urlpatterns = [
    path('', book_list, name='book_list'),
    path('<int:book_id>/', book_detail, name='book_detail'),
    path('add-review/', add_review, name='add_review'),
]