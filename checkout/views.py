from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from store.models import ItemTag
from cart.views import Cart
from .forms import OrderCreateForm
from .models import Order, OrderItem, ShippingAddress


@login_required
def checkout(request):
    """
    Представление чекаута.
    """
    cart = Cart.objects.get(user=request.user)
    page_obj_2 = ItemTag.objects.all()
    tags = ItemTag.objects.all().order_by('name')
    form = OrderCreateForm()
    context = {'cart': cart,
                'form': form,
                'page_obj_2': page_obj_2,
                'tags': tags,
                }

    return render(request, 'checkout/checkout.html', context)


@login_required
def thank_you(request, order_id):
    """
    Страница благодарности за заказ.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'checkout/thank_you.html', {'order': order})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .forms import OrderCreateForm
from django.http import HttpResponse
@login_required
def create_order_whatsapp(request):
    """
    Создание заказа в базе данных и отправка пользователя на WhatsApp.
    """
    cart = get_object_or_404(Cart, user=request.user)

    if cart.items.exists() and request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Создаем заказ в базе данных
            order = Order.objects.create(
                payment_method=form.cleaned_data['payment_method'],
                user=request.user,
            )

            # Создаем адрес доставки
            ShippingAddress.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                order=order,
            )

            # Добавляем товары из корзины в заказ
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    price=cart_item.item.price
                )

            # Очищаем корзину
            cart.clear()

    else:
        form = OrderCreateForm()

    messages.warning(
        request, 'Форма не была корректно обработана, введите данные еще раз'
    )
    context = {'form': form, 'cart': cart}
    return render(request, 'checkout/checkout.html', context)