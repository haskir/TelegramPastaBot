from aiogram.utils.keyboard import (InlineKeyboardBuilder, InlineKeyboardButton)


subscribe_button = InlineKeyboardButton(text="Подписаться", callback_data="Subscribe")
unsubscribe_button = InlineKeyboardButton(text="Отписаться", callback_data="Unsubscribe")
more_button = InlineKeyboardButton(text="Пасту хочу", callback_data="More")


subscribe_keyboard = InlineKeyboardBuilder()
unsubscribe_keyboard = InlineKeyboardBuilder()

subscribe_keyboard.row(subscribe_button, more_button)
unsubscribe_keyboard.row(unsubscribe_button, more_button)