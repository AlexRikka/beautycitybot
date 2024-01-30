from django.db import models


class Client(models.Model):
    """Клиент."""
    username = models.CharField(
        max_length=50,
        unique=True,
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
    )
    phone_number = models.CharField(
        max_length=12,
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Administrator(models.Model):
    """Администратор."""
    first_name = models.CharField(
        max_length=50,
    )
    last_name = models.CharField(
        max_length=50,
    )
    orders = models.IntegerField(
        default=0,
    )

    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'

    def __str__(self):
        return f'{self.first_name} {self.first_name}'

    def display_saloon(self):
        """Вывести название салона в котором работает администратор."""
        return f'{self.saloon}'

    def add_order(self):
        """Засчитать администратору обработанный заказ."""
        self.orders += 1


class Service(models.Model):
    """Услуга."""
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    duration = models.DurationField(
        null=True,
        blank=True,
    )
    price = models.IntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Saloon(models.Model):
    """Салон красоты."""
    name = models.CharField(
        max_length=100,
    )
    admininstrator = models.OneToOneField(
        Administrator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='saloon',
    )
    services = models.ManyToManyField(
        Service,
        related_name='saloons',
        blank=True,
    )

    class Meta:
        verbose_name = 'Салон'
        verbose_name_plural = 'Салоны'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Master(models.Model):
    """Мастер."""
    name = models.CharField(
        max_length=100,
    )
    services = models.ManyToManyField(
        Service,
        related_name='masters',
        blank=True,
    )
    saloons = models.ManyToManyField(
        Saloon,
        related_name='saloon_masters',
        blank=True,
    )

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


# class Day(models.Model):
#     """Модель дня записи."""
#     date = models.DateField()

#     class Meta:
#         verbose_name = 'Дата'
#         verbose_name_plural = 'Даты'
#         ordering = ('date',)

#     def __str__(self):
#         return self.date.strftime("%d.%m")

#     def is_available(self):
#         list(self.hours).count() < 12


class Sign(models.Model):
    """Запись."""
    saloon = models.ForeignKey(
        Saloon,
        on_delete=models.CASCADE,
        related_name='saloon_signs'
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name='master_signs',
        blank=True,
        null=True,
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='signs',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='client_signs'
    )
    date = models.DateField(
        null=True
    )
    time = models.TimeField(
        null=True
    )

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ('time',)

    def __str__(self) -> str:
        return (
            f'{self.client} записан в салон {self.saloon}'
            f' к мастеру {self.master}'
        )

    def get_end_time(self):
        """Получить время окончания процедуры."""
        return self.time + self.service.duration


# class Hour(models.Model):
#     """Модель часа записи."""
#     start = models.TimeField()
#     day = models.ForeignKey(
#         Day,
#         related_name='hours',
#         on_delete=models.CASCADE
#     )
#     sign = models.ForeignKey(
#         Sign,
#         related_name='hours',
#         on_delete=models.CASCADE,
#     )

#     class Meta:
#         verbose_name = 'Час'
#         verbose_name_plural = 'Часы'
#         ordering = ('day', 'start', )

#     def __str__(self):
#         return (
#             f'{self.start.strftime("%H:%M")}-'
#             f'{time(self.start.hour + 1).strftime("%H:%M")}'
#         )

#     def get_end(self):
#         return self.start + timedelta(hours=1)
