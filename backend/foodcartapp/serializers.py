from django.utils import timezone

from rest_framework.serializers import ModelSerializer
from .models import Order, OrderItem
from places.models import Place
from places.views import fetch_coordinates
from star_burger.settings import YANDEX_GEOCODER_API_KEY


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'product',
            'quantity'
            ]


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True
        )

    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products'
            ]

    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
            )
        products_fields = validated_data['products']
        products = [OrderItem(order=order, **fields) for fields in products_fields]
        OrderItem.objects.bulk_create(products)

        place, created = Place.objects.update_or_create(
            address=order.address,
            defaults={'created_date': timezone.now()}
            )
        if created:
            customer_coordinates = fetch_coordinates(
                YANDEX_GEOCODER_API_KEY,
                order.address
            )

            place.lon, place.lat = customer_coordinates
            place.save()

        return order
