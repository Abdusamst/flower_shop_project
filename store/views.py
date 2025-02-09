from django.shortcuts import render
from .models import Item, ItemTag, Favorite
from .paginator import paginator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required

def store(request):
    items = Item.objects.filter(is_available=True)
    tags = ItemTag.objects.all().order_by('name')  # Добавим сортировку
    favorites = Favorite.objects.filter(user=request.user).values_list('item_id', flat=True) if request.user.is_authenticated else []
    context = {
        'page_obj': paginator(request, items, 9),
        'page_obj_2': tags,  # Обновим контекст для тегов
        'range': [*range(1, 7)],  # For random css styles
        'favorites': favorites,
    }
    return render(request, 'store/main_page.html', context)


@receiver(pre_save, sender=Item)
def create_slug(sender, instance, **kwargs):
    if not instance.slug:  # проверяем, есть ли уже slug
        instance.slug = slugify(instance.title)  # Используем title вместо name

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from checkout.models import Order
from .models import Item, ItemTag, Review, Favorite

def item_details(request, item_slug):
    item = get_object_or_404(Item, slug=item_slug)
    tags = ItemTag.objects.all().order_by('name')
    is_favorite = False
    has_bought = False  # Установим False по умолчанию
    reviews = item.reviews.all()
    average_rating = item.average_rating()  # Добавил расчет среднего рейтинга
    user_has_reviewed = False  # Добавил проверку, оставил ли пользователь отзыв
    

    if request.user.is_authenticated:
        has_bought = Order.objects.filter(
            user=request.user,
            items__item=item,  # Убедись, что `items__item` соответствует реальной связи в модели
            status='delivered'  # Убедись, что статус точно такой же в БД
        ).exists()
        is_favorite = Favorite.objects.filter(user=request.user, item=item).exists()
        user_has_reviewed = reviews.filter(user=request.user).exists()

    similar_items = Item.objects.filter(
        Q(tags__in=item.tags.all()) |
        Q(title__icontains=item.title.split()[0])
    ).exclude(id=item.id).distinct()[:4]

    context = {
        'page_obj_2': tags,
        'item': item,
        'is_favorite': is_favorite,
        'similar_items': similar_items,
        'reviews': reviews,
        'has_bought': has_bought,
        'average_rating': average_rating,  # Передаем средний рейтинг в контекст
        'user_has_reviewed': user_has_reviewed,  # Передаем информацию о наличии отзыва
    }
    return render(request, 'store/item_details.html', context)

@login_required
def add_review(request, item_slug):
    item = get_object_or_404(Item, slug=item_slug)
    
    
    has_bought = Order.objects.filter(
        user=request.user, 
        items__item=item,
        status='delivered'
    ).exists()
    

    if not has_bought:
        messages.error(request, 'Вы можете оставить отзыв только после покупки товара.')
        return redirect('store:item_details', item_slug=item.slug)

    if request.method == 'POST':
        
        text = request.POST.get('text')
        rating = request.POST.get('rating')
        image = request.FILES.get('image')
        
        
        if not text or not rating:
            print("Missing required fields")  # Отладочная информация
            messages.error(request, 'Пожалуйста, заполните все обязательные поля.')
            return redirect('store:item_details', item_slug=item.slug)
        
        try:
            review = Review.objects.create(
                item=item,
                user=request.user,
                text=text,
                rating=rating,
                images=image
            )
            messages.success(request, 'Спасибо! Ваш отзыв успешно добавлен.')
        except Exception as e:
            messages.error(request, f'Произошла ошибка при сохранении отзыва: {str(e)}')
            
    return redirect('store:item_details', item_slug=item.slug)

from django.shortcuts import render, get_object_or_404
from .models import Item, Review

def all_reviews(request, item_slug):  # Используйте item_slug
    item = get_object_or_404(Item, slug=item_slug)
    reviews = Review.objects.filter(item=item)
    average_rating = item.average_rating()

    context = {
        'item': item,
        'reviews': reviews,
        'average_rating': average_rating,
    }
    return render(request, 'store/all_reviews.html', context)

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import ItemTag, Item

def tag_details(request, slug):
    tag = get_object_or_404(ItemTag, slug=slug)
    items = Item.objects.filter(tags=tag)  # Вместо tags__in=[tag]
    paginator = Paginator(items, 10)  # отобразить 10 товаров на странице

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')

    context = {
        'tag': tag,
        'page_obj': page_obj,
        'tags': tags,
        'page_obj_2': tags,
    }

    return render(request, 'store/tag_details.html', context)


def tag_list(request):
    tags = ItemTag.objects.all()
    for tag in tags:
        tag.description = _(tag.description)
        tag.name = _(tag.name)
    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')
    context = {
        'page_obj': paginator(request, tags, 6),                                                                                                        
        'tags': tags,
        'page_obj_2': tags,
    }
    return render(request, 'store/tag_list.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import Favorite, Item

@login_required
def add_to_favorites(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    Favorite.objects.get_or_create(user=request.user, item=item)
    return redirect(reverse('store:item_details', kwargs={'item_slug': item.slug}))

@login_required
def remove_from_favorites(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    favorite = get_object_or_404(Favorite, user=request.user, item=item)
    favorite.delete()
    return redirect(reverse('store:item_details', kwargs={'item_slug': item.slug}))

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')
    context = {
        'tags': tags,
        'page_obj_2': tags,
        'favorites': favorites
    }
    return render(request, 'store/favorite_list.html', context)




from django.http import JsonResponse

@login_required
def toggle_favorite(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, item=item)
    if not created:
        favorite.delete()
        action = 'removed'
    else:
        action = 'added'
    return JsonResponse({'action': action})

from django.db.models import Q
from django.shortcuts import render
from .models import Item, ItemTag

def search(request):
    query = request.GET.get('q')
    if query:
        results = Item.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    else:
        results = Item.objects.all()  # Показываем все товары, если запрос пуст
    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')
    context = {
        'tags': tags,
        'page_obj_2': tags,
        'query': query,
        'results': results,
    }
    return render(request, 'store/search.html', context)


from .forms import SellerRegistrationForm

from django.shortcuts import render, redirect
from .forms import SellerRegistrationForm, ItemForm
from .models import Seller, Item

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SellerRegistrationForm
from .models import User, Seller, ItemTag
import urllib.parse

@login_required
def become_seller(request):
    if hasattr(request.user, 'seller'):
        messages.info(request, 'Вы уже являетесь продавцом.')
        return redirect('store:home')
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        store_name = request.POST.get('store_name')
        store_type = request.POST.get('store_type')
        store_address = request.POST.get('store_address')
        
        if phone_number and store_name and store_type and store_address:
            Seller.objects.create(
                user=request.user,
                phone_number=phone_number,
                store_name=store_name,
                store_type=store_type,
                store_address=store_address
            )
            messages.success(request, 'Поздравляем! Вы стали продавцом.')
            return redirect('store:home')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля.')
    
    return render(request, 'store/becomeseller.html')



@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user  
            item.save()
            return redirect('store:my_items')
    else:
        form = ItemForm()

    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')
    context = {
        'form': form,
        'tags': tags,
        'page_obj_2': tags,
    }
    return render(request, 'store/add_item.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, ItemTag
from checkout.models import OrderItem
from cart.models import CartItem

@login_required
def my_items(request):
    seller = request.user
    items = Item.objects.filter(seller=seller)

    context = {
        'items': items,
        'tags': ItemTag.objects.all().order_by('name'),
        'page_obj_2': ItemTag.objects.all(),
    }
    return render(request, 'store/my_items.html', context)


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)  # Используйте объект CustomUser вместо Seller
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('store:my_items')
    else:
        form = ItemForm(instance=item)

    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')
    context = {
        'item': item,
        'form': form,
        'tags': tags,
        'page_obj_2': tags,
    }
    return render(request, 'store/edit_item.html', context)

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('store:my_items')
    
    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')
    context = {
        'item': item,
        'tags': tags,
        'page_obj_2': tags,
    }
    return render(request, 'store/delete_item.html', context)



