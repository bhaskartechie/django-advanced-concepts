from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, UserRecordView

router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/record-user/', UserRecordView.as_view(), name='record_user'),
]
