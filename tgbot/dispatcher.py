from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
from . import handlers


def setup_dispatcher(dp):
    # start
    dp.add_handler(CommandHandler("start", handlers.start_callback))
    # usage
    dp.add_handler(CommandHandler("use_call", handlers.use_call))
    dp.add_handler(CommandHandler("use_bot", handlers.use_bot))
    dp.add_handler(CommandHandler(
        "pdconsent_agreed", handlers.pdconsent_agreed))
    dp.add_handler(CommandHandler(
        "pdconsent_refuse", handlers.pdconsent_refuse))

    # location
    dp.add_handler(CommandHandler("show_locations", handlers.show_locations))

    # masters
    dp.add_handler(CommandHandler("show_masters", handlers.show_masters))

    # services
    dp.add_handler(CommandHandler("show_services", handlers.show_services))

    # prices
    dp.add_handler(CommandHandler("show_prices", handlers.show_prices))

    # date and time
    dp.add_handler(CommandHandler("show_days", handlers.show_days))
    dp.add_handler(CommandHandler("show_hours", handlers.show_hours))

    # registration
    dp.add_handler(CommandHandler(
        "ask_phone_number", handlers.ask_phone_number))
    dp.add_handler(CommandHandler(
        "registration_success", handlers.registration_success))

    # show_saloon_services callback
    dp.add_handler(CallbackQueryHandler(
        handlers.show_saloon_services,
        pattern=r'^show_saloon_services\s[0-9]+',
    ))

    # show_master_saloons callback
    dp.add_handler(CallbackQueryHandler(
        handlers.show_master_saloons,
        pattern=r'^show_master_saloons\s[0-9]+',
    ))

    # show_master_services_in_saloon callback
    dp.add_handler(CallbackQueryHandler(
        handlers.show_master_services_in_saloon,
        pattern=r'^show_master_services_in_saloon\s[0-9]+\s[0-9]+',
    ))

    # show_service_saloons
    dp.add_handler(CallbackQueryHandler(
        handlers.show_service_saloons,
        pattern=r'^show_service_saloons\s[0-9]+',
    ))

    # show_days callback
    dp.add_handler(CallbackQueryHandler(
        handlers.show_days,
        pattern=r'^show_days\s[0-9]+',
    ))

    # catch phone number
    dp.add_handler(MessageHandler(
        Filters.regex("(^[+0-9]{1,3})*([0-9]{10,11}$)"),
        handlers.registration_success,
    ))

    # any callback
    dp.add_handler(CallbackQueryHandler(handlers.callback_handler))

    return dp
