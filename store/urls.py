from django.urls import path
from .views import item_details, store, tag_details, tag_list, add_to_favorites, remove_from_favorites, favorite_list, toggle_favorite, search, become_seller, add_item, add_review, all_reviews
from . import views
from django.urls import re_path
app_name = 'store'

urlpatterns = [
    path('', store, name='home'),
    path('categories/', tag_list, name='tag_list'),
    re_path(r'^category-details/(?P<slug>[\w-]+)/$', tag_details, name='tag_details'),
    path('search/', search, name='search'),  # Маршрут для поиска
    path('favorites/', favorite_list, name='favorite_list'),  # Маршрут для списка избранного
    path('add_to_favorites/<int:item_id>/', add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:item_id>/', remove_from_favorites, name='remove_from_favorites'),
    path('toggle_favorite/<int:item_id>/', toggle_favorite, name='toggle_favorite'),
    path('become-seller/', become_seller, name='becomeseller'),  # Маршрут для регистрации продавца
    path('add_item/', add_item, name='add_item'),
    path('<slug:item_slug>/reviews/', views.all_reviews, name='all_reviews'),
    path('my_items/', views.my_items, name='my_items'),  # Добавляем путь к "Мои товары"
    path('edit_item/<int:item_id>/', views.edit_item, name='edit_item'),  # Добавляем путь к редактированию товара
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),  # Добавляем путь к удалению товара
    path('<slug:item_slug>/', item_details, name='item_details'),  # Маршрут для деталей товара
    path('<slug:item_slug>/add_review/', views.add_review, name='add_review'),

]

