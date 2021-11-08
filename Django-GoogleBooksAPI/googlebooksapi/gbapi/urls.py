from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-book', views.add_book, name='add-book'),
    path('confirm-overwriting', views.confirm_overwriting, name='confirm-overwriting'),
    path('import-from-API', views.import_book, name='import-from-API'),
    path('edit-book/<id>', views.edit_book, name='edit-book'),
    path('api/query', views.api_request, name='api'),
]