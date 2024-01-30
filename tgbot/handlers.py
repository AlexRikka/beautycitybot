import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from saloons.models import Client, Master, Saloon, Service, Sign


def callback_handler(update, context):
    """Запуск команд отловленных CallbackQueryHandler-ом."""
    COMMANDS = {
        'use_call': use_call,
        'use_bot': use_bot,
        'ask_pdconsent': ask_pdconsent,
        'pdconsent_refuse': pdconsent_refuse,
        'show_locations': show_locations,
        'show_masters': show_masters,
        'show_services': show_services,
        'show_prices': show_prices,
        'show_days': show_days,
        'show_hours': show_hours,
        'ask_phone_number': ask_phone_number,
    }
    COMMANDS[update.callback_query.data](update, context)


def create_keyboard(queryset):
    """Создает вертикальную клавиатуру с наименованиями объектов из Queryset"""
    keyboard = [
        [InlineKeyboardButton(
            item.name,
            callback_data=item.name
        )] for item in queryset
    ]
    return InlineKeyboardMarkup(keyboard)


# start
def start_callback(update, context):
    """Стартовый вопрос."""
    global client_choices
    client_choices = {
        'username': update.message.from_user['username'],
        'user_id': update.message.from_user['id'],
        'first_name': update.message.from_user['first_name'],
        'phone_number': None,
        'saloon_id': None,
        'master_id': None,
        'service_id': None,
        'date': None,
        'time': None,
    }

    Client.objects.get_or_create(
            username=client_choices['username'],
            first_name=client_choices['first_name'],
        )
    # new_client.save()
    update.message.reply_text(
        "Добро пожаловать в салон BeautyCity!\n" +
        "Выберите как вы хотите записаться на процедуру.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "В боте 🤖",
                callback_data="use_bot"
            ),
            InlineKeyboardButton(
                "Через менеджера ☎️",
                callback_data='use_call'
            ),
        ]])
    )


# usage
def use_call(update, context):
    """Вывести контакты менеджера."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Запишитесь на процедуру у нашего менеджера по номеру"
              "+79371234567")
    )


def use_bot(update, context):
    """Вывести вопрос о согласии обработки персональных данных."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Подтвердите согласие на обработку персональных данных",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "✅",
                callback_data="ask_pdconsent"
            ),
            InlineKeyboardButton(
                "❌",
                callback_data='pdconsent_refuse'
            ),
        ]])
    )


def ask_pdconsent(update, context):
    """Отправить типовое согласие на обработку персональных данных."""
    doc_path = r'./assets/Согласие на обработку персональных данных.pdf'
    with open(doc_path, 'rb') as f:
        context.bot.sendDocument(chat_id=update.effective_chat.id, document=f)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите вариант поиска",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "По салону",
                callback_data="show_locations"
            ),
            InlineKeyboardButton(
                "По мастеру",
                callback_data='show_masters'
            ),
            InlineKeyboardButton(
                "По услуге",
                callback_data='show_services'
            ),
        ]])
    )


def pdconsent_refuse(update, context):
    """Попрощаться после отказа предоставления персональных данных."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Досвидания"
    )


# location
def show_locations(update, context):
    """Вывести список салонов."""
    saloons = Saloon.objects.all()
    keyboard = [
        [InlineKeyboardButton(
            saloon.name,
            callback_data=f'show_saloon_services {saloon.id}'
        )] for saloon in saloons
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Список салонов:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# masters
def show_masters(update, context):
    """Вывести список мастеров."""
    masters = Master.objects.all()
    keyboard = [
        [InlineKeyboardButton(
            master.name,
            callback_data=f'show_master_saloons {master.id}'
        )] for master in masters
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Наши мастера:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# services
def show_services(update, context):
    """Вывести список услуг."""
    services = Service.objects.all()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Наши услуги:",
        reply_markup=create_keyboard(services)
    )


def show_saloon_services(update, context):
    """Показать услуги доступные в салоне."""
    saloon_id = update.callback_query.data.split()[1]
    client_choices['saloon_id'] = saloon_id
    saloon_services = Service.objects.filter(saloons=saloon_id)
    saloon_services_keyboard = [
        [InlineKeyboardButton(
            service.name,
            callback_data=f'show_days_any_master {service.id}'
        )] for service in saloon_services]
    saloon_services_keyboard.append(
        [InlineKeyboardButton(
            'Показать цены на все услуги',
            callback_data='show_prices',)])
    price_list = '\n'.join(
        f'{service.name} - {service.price}р.' for service in saloon_services)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Услуги салона {Saloon.objects.get(id=saloon_id)}:\n' +
             f'{price_list}',
        reply_markup=InlineKeyboardMarkup(saloon_services_keyboard)
    )


def show_master_saloons(update, context):
    """Показать салоны в которых работает мастер."""
    master_id = update.callback_query.data.split()[1]
    client_choices['master_id'] = master_id
    master_saloons = Saloon.objects.filter(saloon_masters=master_id)
    keyboard = [
        [InlineKeyboardButton(
            saloon.name,
            callback_data=f'show_master_services_in_saloon {saloon.id}'
        )] for saloon in master_saloons
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'{Master.objects.get(id=master_id)} работает в салонах:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def show_master_services_in_saloon(update, context):
    """Показать услуги, которые оказывает мастер в определенном салоне."""
    saloon_id = update.callback_query.data.split()[1]
    client_choices['saloon_id'] = saloon_id
    master_id = client_choices['master_id']
    services = Service.objects.filter(
        masters=client_choices['master_id'],
        saloons=saloon_id
    )
    keyboard = [
        [InlineKeyboardButton(
            service.name,
            callback_data=f'show_days {service.id}'
        )] for service in services
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Услуги мастера {Master.objects.get(id=master_id)} '
             f'в салоне {Saloon.objects.get(id=saloon_id)}:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# prices
def show_prices(update, context):
    """Показать цены на все услуги сети."""
    services = Service.objects.all()
    price_list = '\n'.join(
        f'{service.name} - {service.price}р.' for service in services)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Цены на наши услуги:\n" + price_list,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Выбрать услугу",
                        callback_data="show_services"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Позвонить менеджеру ☎️",
                        callback_data='use_call'
                    ),
                ]
            ]))


# date and time
def show_days(update, context):
    service_id = update.callback_query.data.split()[1]
    client_choices['service_id'] = service_id
    today = datetime.datetime.today()
    next_two_weeks = [
        today + datetime.timedelta(days=1) * i for i in range(14)]
    signs = Sign.objects.filter(
        master=Master.objects.get(id=client_choices['master_id']),
    )
    schedule = {}
    for sign in signs:
        date = sign.date.strftime("%d.%m")
        time = sign.time.hour
        if date not in schedule:
            schedule[date] = []
        for i in range(sign.service.duration.seconds // 3600):
            schedule[date].append(f'{time + i}:00-{time + i + 1}:00')
    booked_days = []
    for date, intervals in schedule.items():
        if len(intervals) >= 12:
            booked_days.append(date)
    free_days = []
    for day in next_two_weeks:
        if not (day.strftime("%d.%m") in booked_days):
            free_days.append(day)
    keyboard = [
        [InlineKeyboardButton(
            day.strftime("%d.%m"),
            callback_data=f'show_hours {day.day} {day.month}'
        )] for day in free_days
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите день:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def show_days_any_master(update, context):
    service_id = update.callback_query.data.split()[1]
    client_choices['service_id'] = service_id
    today = datetime.datetime.today()
    next_two_weeks = [
        today + datetime.timedelta(days=1) * i for i in range(14)]
    masters = Master.objects.filter(
        services=Service.objects.get(id=service_id),
        saloons=Saloon.objects.get(id=client_choices['saloon_id']),
    )
    signs = Sign.objects.filter(
        service=Service.objects.get(id=service_id),
        saloon=Saloon.objects.get(id=client_choices['saloon_id'])
    )
    schedule = {}
    for master in masters:
        signs = Sign.objects.filter(
            saloon=Saloon.objects.get(id=client_choices['saloon_id']),
            master=master,
        )
        for sign in signs:
            date = sign.date.strftime("%d.%m")
            time = sign.time.hour
            if date not in schedule:
                schedule[date] = []
            for i in range(sign.service.duration.seconds // 3600):
                schedule[date].append(f'{time + i}:00-{time + i + 1}:00')
    booked_days = []
    for date, intervals in schedule.items():
        if len(intervals) >= 12:
            booked_days.append(date)
    free_days = []
    for day in next_two_weeks:
        if not (day.strftime("%d.%m") in booked_days):
            free_days.append(day)
    keyboard = [
        [InlineKeyboardButton(
            day.strftime("%d.%m"),
            callback_data=f'show_hours_any_master {day.day} {day.month}'
        )] for day in free_days
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите день:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def show_hours(update, context):
    day = int(update.callback_query.data.split()[1])
    month = int(update.callback_query.data.split()[2])
    date = datetime.date(
        day=day, month=month, year=datetime.datetime.today().year)
    client_choices['date'] = date
    hours = [datetime.time(i) for i in range(9, 21)]
    signs = Sign.objects.filter(
        master=Master.objects.get(id=client_choices['master_id']),
        date=date,
    )
    print(signs)
    booked_hours = []
    for sign in signs:
        time = sign.time.hour
        for i in range(sign.service.duration.seconds // 3600):
            booked_hours.append(f'{time + i}:00')
    print(booked_hours)
    free_hours = []
    for hour in hours:
        if not (hour.strftime('%H:%M') in booked_hours):
            free_hours.append(hour)
    keyboard = [
        [InlineKeyboardButton(
            (f'{hour.strftime("%H:%M")}-'
             f'{datetime.time(hour.hour + 1).strftime("%H:%M")}'),
            callback_data=f'ask_phone_number {hour.hour}'
        )] for hour in free_hours
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите время:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def show_hours_any_master(update, context):
    day = int(update.callback_query.data.split()[1])
    month = int(update.callback_query.data.split()[2])
    date = datetime.date(
        day=day, month=month, year=datetime.datetime.today().year)
    client_choices['date'] = date
    hours = [datetime.time(i) for i in range(9, 21)]
    signs = Sign.objects.filter(
        service=Service.objects.get(id=client_choices['service_id']),
        saloon=Saloon.objects.get(id=client_choices['saloon_id']),
        date=date,
    )
    print(signs)
    booked_hours = []
    for sign in signs:
        time = sign.time.hour
        for i in range(sign.service.duration.seconds // 3600):
            booked_hours.append(f'{time + i}:00')
    print(booked_hours)
    free_hours = []
    for hour in hours:
        if not (hour.strftime('%H:%M') in booked_hours):
            free_hours.append(hour)
    keyboard = [
        [InlineKeyboardButton(
            (f'{hour.strftime("%H:%M")}-'
             f'{datetime.time(hour.hour + 1).strftime("%H:%M")}'),
            callback_data=f'ask_phone_number {hour.hour}'
        )] for hour in free_hours
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите время:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# registration
def ask_phone_number(update, context):
    hour = int(update.callback_query.data.split()[1])
    client_choices['time'] = datetime.time(hour)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите номер телефона",
    )


def registration_success(update, context):
    client_choices['phone_number'] = update.message.text
    current_user = Client.objects.get(username=client_choices['username'])
    Client.objects.filter(
        username=client_choices['username']
    ).update(phone_number=client_choices['phone_number'])
    if client_choices['master_id']:
        new_sign = Sign.objects.create(
            saloon=Saloon.objects.get(id=client_choices['saloon_id']),
            master=Master.objects.get(id=client_choices['master_id']),
            service=Service.objects.get(id=client_choices['service_id']),
            client=current_user,
            date=client_choices['date'],
            time=client_choices['time'],
        )
    else:
        new_sign = Sign.objects.create(
            saloon=Saloon.objects.get(id=client_choices['saloon_id']),
            service=Service.objects.get(id=client_choices['service_id']),
            client=current_user,
            date=client_choices['date'],
            time=client_choices['time'],
        )
    new_sign.save()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы успешно записаны на процедуру!",
    )
