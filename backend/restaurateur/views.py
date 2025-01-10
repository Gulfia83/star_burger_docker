from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from requests.exceptions import RequestException
import requests
from geopy import distance

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from places.models import Place
from places.views import fetch_coordinates
from star_burger.settings import YANDEX_GEOCODER_API_KEY


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects \
        .exclude(status__in=['end']) \
        .prefetch_related('restaurant', 'items') \
        .order_by('status').get_total_price()

    menu_items = RestaurantMenuItem.objects\
        .filter(availability=True)\
        .prefetch_related('restaurant',
                          'product')
    restaurants = Restaurant.objects.all()
    places = Place.objects.all()

    for order in orders:
        for item in order.items.select_related('product'):
            available_restaurants = menu_items\
                .filter(product=item.product)\
                .values_list('restaurant__name', flat=True)
        order.restaurants = available_restaurants

        order_place = places.get(address=order.address)
        customer_coordinates = order_place.lat, order_place.lon
            
        restaurant_distances = []
        for restaurant in order.restaurants:
            restaurant = restaurants.get(name=restaurant)
            restaurant_place = places.get(address=restaurant.address)
            restaurant_coordinates = restaurant_place.lat, restaurant_place.lon
            if customer_coordinates and restaurant_coordinates:
                restaurant_distance = round(distance.distance(
                    customer_coordinates,
                    restaurant_coordinates).km, 2)
            restaurant_distances.append((restaurant, restaurant_distance))
        order.restaurant_distances = sorted(
                    restaurant_distances, key=lambda x: x[1]
                )

    return render(request,
                  template_name='order_items.html',
                  context={'order_items': orders}
                  )
