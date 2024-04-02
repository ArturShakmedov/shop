from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import *


def send_contact_button():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_1 = KeyboardButton(text='Поделится контактом', request_contact=True)
    markup.row(buttons_1)
    return markup


# def quantity_image():
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     buttons_1 = KeyboardButton(text='1️⃣')
#     buttons_2 = KeyboardButton(text='2️⃣')
#     buttons_3 = KeyboardButton(text='3️⃣')
#     buttons_4 = KeyboardButton(text='4️⃣')
#     buttons_5 = KeyboardButton(text='5️⃣')
#     buttons_6 = KeyboardButton(text='6️⃣')
#     buttons_7 = KeyboardButton(text='7️⃣')
#     buttons_8 = KeyboardButton(text='8️⃣')
#     buttons_9 = KeyboardButton(text='9️⃣')
#     buttons_10 = KeyboardButton(text='🔟')
#     markup.row(buttons_1, buttons_2, buttons_3)
#     markup.row(buttons_4, buttons_5, buttons_6)
#     markup.row(buttons_7, buttons_8, buttons_9)
#     markup.row(buttons_10)
#     return markup


# def adin_main_menu():
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     buttons_1 = KeyboardButton(text='Мену')
#     buttons_2 = KeyboardButton(text='Каталог')
#     buttons_3 = KeyboardButton(text='Скидки')
#     buttons_4 = KeyboardButton(text='Карзина')
#     buttons_5 = KeyboardButton(text='История')
#     buttons_6 = KeyboardButton(text='Добавит Товар')
#     buttons_7 = KeyboardButton(text='Удалить товар')
#     markup.row(buttons_1)
#     markup.row(buttons_2, buttons_3)
#     markup.row(buttons_4, buttons_5)
#     markup.row(buttons_5, buttons_6)
#     return markup


def generate_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_1 = KeyboardButton(text='меню 🔄')
    buttons_2 = KeyboardButton(text='Каталог')
    buttons_3 = KeyboardButton(text='скидки 🎁')
    buttons_4 = KeyboardButton(text='Карзина 🧺')
    buttons_5 = KeyboardButton(text='История')
    markup.row(buttons_1)
    markup.row(buttons_2, buttons_3)
    markup.row(buttons_4, buttons_5)
    return markup


def generate_category_menu_admin():
    markup = InlineKeyboardMarkup(row_width=2)
    categories = get_all_categories()
    buttons = []
    for category in categories:
        btn = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        buttons.append(btn)
    markup.row(InlineKeyboardButton(text='Добавить категорию', callback_data='add_categories'),
               InlineKeyboardButton(text='Удалить категорию', callback_data='delete_categories'))
    markup.add(*buttons)
    return markup


def generate_category_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    categories = get_all_categories()
    buttons = []
    for category in categories:
        btn = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def generate_products_by_category_admin(category_id):
    markup = InlineKeyboardMarkup(row_width=2)
    products = get_products_by_category_id(category_id)
    button = []
    for product in products:
        btn = InlineKeyboardButton(text=product[1], callback_data=f'product_{product[0]}')
        button.append(btn)

    markup.add(*button)
    markup.row(InlineKeyboardButton(text='Добавить продукт', callback_data=f'add_tovar_{category_id}'),
               InlineKeyboardButton(text='Удалить продукт', callback_data=f'delete_tovar_{category_id}'))
    markup.row(
        InlineKeyboardButton(text='Назад', callback_data='back'),
        InlineKeyboardButton(text='Меню', callback_data='main_menu'),
        InlineKeyboardButton(text='Далее', callback_data='next')
    )
    return markup


def generate_products_by_category(category_id):
    markup = InlineKeyboardMarkup(row_width=2)
    products = get_products_by_category_id(category_id)
    button = []
    for product in products:
        btn = InlineKeyboardButton(text=product[1], callback_data=f'product_{product[0]}')
        button.append(btn)
    markup.add(*button)
    markup.row(
        InlineKeyboardButton(text='Назад', callback_data='back'),
        InlineKeyboardButton(text='Меню', callback_data='main_menu'),
        InlineKeyboardButton(text='Далее', callback_data='next')
    )
    return markup


def generate_product_detail_menu(product_id, category_id, cart_id, product_name='', c=0):
    markup = InlineKeyboardMarkup(row_width=3)
    try:
        quantity = get_quantity(cart_id, product_name)
    except:
        quantity = c

    buttons = []
    btn_back = InlineKeyboardButton(text=str('Назад'), callback_data=f'back_{quantity}_{product_id}')
    btn_quantity = InlineKeyboardButton(text=str(quantity), callback_data=f'coll')
    btn_next = InlineKeyboardButton(text=str('Далее'), callback_data=f'next_{quantity}_{product_id}')
    buttons.append(btn_back)
    buttons.append(btn_quantity)
    buttons.append(btn_next)
    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton(text='Добавить в корзину', callback_data=f'cart_{product_id}_{quantity}')
    )
    markup.row(
        InlineKeyboardButton(text='Меню', callback_data=f'menu_{category_id}')
    )
    return markup


def generate_cart_menu(cart_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text='Оформить заказ', callback_data=f'order_{cart_id}')
    )
    cart_products = get_carts_products_for_delete(cart_id)
    for cart_product_id, product_name in cart_products:
        markup.row(
            InlineKeyboardButton(text=f'Удалить {product_name}', callback_data=f'delete_{cart_product_id}')
        )
    return markup
