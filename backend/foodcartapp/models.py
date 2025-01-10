from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from phonenumber_field.modelfields import PhoneNumberField


STATUSES = [
    ('under', 'на рассмотрении'),
    ('todo', 'принят в работу'),
    ('delivery', 'передан в доставку'),
    ('end', 'завершен')
]


PAYMENTS = [
    ('cash', 'наличностью'),
    ('noncash', 'электронно'),
    ('unspecified', 'не указано')
]


class OrderQuerySet(models.QuerySet):
    def get_total_price(self):
        total_price = self.annotate(
            order_sum=Sum(
                F('items__price') * F('items__quantity')
                )
            )
        return total_price
    

class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    firstname = models.CharField(
        max_length=50,
        verbose_name='Имя',
        db_index=True
    )
    lastname = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        db_index=True
    )
    phonenumber = PhoneNumberField(
        verbose_name='Мобильный телефон',
        db_index=True
        )
    address = models.CharField(
        max_length=200,
        verbose_name='Адрес',
        db_index=True
    )
    comments = models.TextField(max_length=200,
                                blank=True,
                                verbose_name='Комментарии')
    registered_at = models.DateTimeField(verbose_name='Дата создания',
                                         auto_now=True,
                                         db_index=True)
    called_at = models.DateTimeField(verbose_name='Дата звонка',
                                     blank=True,
                                     null=True,
                                     db_index=True)
    delivered_at = models.DateTimeField(verbose_name='Дата доставки',
                                        blank=True,
                                        null=True,
                                        db_index=True)
    payment_method = models.CharField(max_length=30,
                                      choices=PAYMENTS,
                                      default='unspecified',
                                      verbose_name='Способ оплаты',
                                      db_index=True)
    status = models.CharField(max_length=30,
                              choices=STATUSES,
                              default='under',
                              verbose_name='Статус заказа',
                              db_index=True)
    restaurant = models.ForeignKey(Restaurant,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ресторан',
                                   related_name='orders',
                                   blank=True,
                                   null=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.CASCADE,
        related_name='items'
    )
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        on_delete=models.CASCADE,
        related_name='items'
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True
    )

    class Meta:
        verbose_name = 'Заказанный товар'
        verbose_name_plural = 'Заказанные товары'

    def __str__(self):
        return f'{self.product} - {self.quantity}'