from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

__all__ = [
    "subscribe_button",
    "unsubscribe_button",
    "more_button",
    "subscribe_keyboard",
    "unsubscribe_keyboard",
]


subscribe_button = InlineKeyboardButton(text="Подписаться", callback_data="Subscribe")
unsubscribe_button = InlineKeyboardButton(
    text="Отписаться", callback_data="Unsubscribe"
)
more_button = InlineKeyboardButton(text="Пасту хочу", callback_data="More")


_subscribe_keyboard = InlineKeyboardBuilder()
_unsubscribe_keyboard = InlineKeyboardBuilder()

_subscribe_keyboard.row(subscribe_button, more_button)
_unsubscribe_keyboard.row(unsubscribe_button, more_button)

subscribe_keyboard = _subscribe_keyboard.as_markup()
unsubscribe_keyboard = _unsubscribe_keyboard.as_markup()