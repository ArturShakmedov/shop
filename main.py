import telebot
from telebot.types import Message, CallbackQuery, LabeledPrice
from keybords import *
from database import *
from datetime import datetime


try:
    create_table_users()
    create_table_carts()
    create_cart_products_table()
    create_categories_table()
    create_products_table()
    order()
    orders_total_price()
except:
    pass

bot = telebot.TeleBot('6795553609:AAGg5O6NA3rtPlJLEeYH6a73NvQv0l0VePA')


@bot.message_handler(commands=['start'])
def commands_start(message: Message):
    msg = bot.reply_to(message, f'hi {message.from_user.full_name}', )
    register_user(message)


def register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = first_select_user(chat_id)
    if user:
        bot.reply_to(message, '<em>Авторизация прошла успешна</em>', parse_mode='HTML')
        show_main_menu(message)
    else:
        first_register_user(chat_id, full_name)
        bot.reply_to(message, 'Для регистрации поделитесь Контактом', reply_markup=send_contact_button())


@bot.message_handler(content_types=['contact'])
def finish_register_users(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    update_user_finish_register(phone, chat_id)
    create_cart_for_users(message)
    bot.reply_to(message, 'Регистрация прошла успешно')
    show_main_menu(message)


def create_cart_for_users(message: Message):
    chat_id = message.chat.id
    try:
        insert_to_cart(chat_id)
    except:
        pass


@bot.message_handler(commands=['start_admin'])
def commands_start(message: Message):
    chat_id = message.chat.id
    msg = bot.reply_to(message, f'hi {message.from_user.full_name}, введи пароль', )
    bot.register_next_step_handler(msg, register_admin)


def register_admin(message: Message):
    chat_id = message.chat.id
    if message.text == '123':
        first_register_admin(chat_id)
        bot.send_message(message.chat.id, 'Пароль  введен верно')
        generate_main_menu()
    else:
        bot.send_message(message.chat.id, 'Попробуйте в другой раз')


def show_main_menu(message: Message):
    bot.reply_to(message, 'Выберете действие', reply_markup=generate_main_menu())


@bot.message_handler(regexp=r'каталог')
def make_order(message: Message):
    chat_id = message.chat.id
    admin = first_select_admin(chat_id)
    if admin[0] == 'Yes':
        bot.reply_to(message, 'Выберете модель', reply_markup=generate_category_menu_admin())
    else:
        bot.reply_to(message, 'Выберете модель', reply_markup=generate_category_menu())


@bot.callback_query_handler(lambda call: 'category' in call.data)
def show_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    category_id = int(category_id)
    admin = first_select_admin(chat_id)
    if admin[0] == 'Yes':
        bot.reply_to(call.message, 'Категории', reply_markup=generate_products_by_category_admin(category_id))
    else:
        bot.reply_to(call.message, 'Категории', reply_markup=generate_products_by_category(category_id))


@bot.callback_query_handler(lambda call: 'add_categories' in call.data)
def add_category(call):
    kwargs = bot.send_message(call.message.chat.id, 'Введите название категории')
    bot.register_next_step_handler(kwargs, add_category_finish)


def add_category_finish(message):
    category_name = message.text
    insert_categories(category_name)
    bot.reply_to(message, 'Категория добавлена')


@bot.callback_query_handler(lambda call: 'main_menu' in call.data)
def return_main_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    admin = first_select_admin(chat_id)
    if admin[0] == 'Yes':
        bot.reply_to(call.message, 'Выберете модель', reply_markup=generate_category_menu_admin())
    else:
        bot.reply_to(call.message, 'Выберете модель', reply_markup=generate_category_menu())


@bot.callback_query_handler(lambda call: 'product' in call.data)
def show_detail_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id = call.data.split('_')
    product_id = int(product_id)
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    try:
        quantity = get_quantity(cart_id, product[1])
        if quantity is None:
            quantity = 0
    except:
        quantity = 0

    bot.delete_message(chat_id, message_id)
    bot.send_photo(chat_id=chat_id, photo=f'{product[-2]}', caption=f'''{product[1]}
Ингридиенты: {product[3]}
Цена: {product[2]}''',
                   reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                   category_id=product[-1],
                                                                   cart_id=cart_id, product_name=product[1],
                                                                   c=quantity))


@bot.callback_query_handler(lambda call: 'tovar' in call.data)
def add_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, name, categories_id = call.data.split('_')
    _ = bot.send_message(chat_id, 'Введите название:')
    bot.register_next_step_handler(_, add_product_name, categories_id)


def add_product_name(message, categories_id):
    product_name = message.text
    chat_id = message.chat.id
    _ = bot.send_message(chat_id, 'Введите стоимость')
    bot.register_next_step_handler(_, add_price, categories_id, product_name)


def add_price(message, categories_id, product_name):
    price = int(message.text)
    chat_id = message.chat.id
    _ = bot.send_message(chat_id, 'Напишите описание для данного товара')
    bot.register_next_step_handler(_, add_photo, categories_id, product_name, price)


def add_photo(message, categories_id, product_name, price):
    description = message.text
    chat_id = message.chat.id
    _ = bot.send_message(chat_id, 'Отправьте фото: ')
    bot.register_next_step_handler(_, add_next_photo,  categories_id, product_name, price, description)


def add_next_photo(message, categories_id, product_name, price, description):
    num = 0
    chat_id = message.chat.id
    if message.photo is not None:
        id_photo = message.photo[0].file_id
        insert_product_table(product_name, price, description, id_photo, categories_id)
        print(product_name, price, description, id_photo, categories_id)
        bot.send_message(chat_id, 'Товар добавлен в базу данных:')


@bot.callback_query_handler(lambda call: 'menu' in call.data)
def return_to_category(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    bot.delete_message(chat_id, message_id)
    admin = first_select_admin(chat_id)
    if admin[0] == 'Yes':
        bot.reply_to(call.message, 'Выберете модель', reply_markup=generate_category_menu_admin())
    else:
        bot.reply_to(call.message, 'Выберете модель', reply_markup=generate_category_menu())


@bot.callback_query_handler(lambda call: 'next' in call.data)
def add_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    quantity += 1
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                             caption=f'''{product[1]} 
Ингридиенты: {product[3]} 

Цена: {product[2]}''', reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                 category_id=product[-1],
                                                                 cart_id=cart_id, c=quantity))


@bot.callback_query_handler(lambda call: 'back' in call.data)
def remove_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    if quantity <= 0:
        bot.answer_callback_query(call.id, 'Ниже нуля нельзя')
        pass
    else:
        quantity -= 1
        bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                                 caption=f'''{product[1]} 
Ингридиенты: {product[3]} 

Цена: {product[2]}''', reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                 category_id=product[-1],
                                                                 cart_id=cart_id, c=quantity))


@bot.callback_query_handler(lambda call: 'cart' in call.data)
def add_choose_product_to_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)

    cart_id = get_user_cart_id(chat_id)
    product = get_product_detail(product_id)
    final_price = product[2] * quantity

    if insert_or_update_cart_product(cart_id, product[1], quantity, final_price):
        bot.answer_callback_query(call.id, 'Товар в корзине')
    else:
        bot.answer_callback_query(call.id, 'Количество успешно изменено')


@bot.message_handler(regexp='Карзина 🧺')
def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)

    try:
        update_total_product_total_price(cart_id)
    except Exception as e:
        bot.reply_to('Карзина не доступна. Обратитесь в тех поддержку')
        return

    cart_product = get_cart_products(cart_id)
    total_products, total_price = get_total_products_price(cart_id)

    text = 'Ваша корзина \n\n'
    i = 0
    for product_name, quantity, final_price in cart_product:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price}\n\n'''

    text += f'''Общее количество продуктов: {0 if total_products is None else total_products}  
Общая стоимость счета: {0 if total_price is None else total_price}'''
    if edit_message:
        bot.edit_message_text(text, chat_id, message.message_id, reply_markup=generate_cart_menu(cart_id))
    else:
        bot.send_message(chat_id, text, reply_markup=generate_cart_menu(cart_id))


@bot.callback_query_handler(lambda call: 'delete' in call.data)
def delete_cart_products(call: CallbackQuery):
    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)
    message = call.message

    delete_cart_products_from(cart_product_id)

    bot.answer_callback_query(call.id, text='Продукт успешно удален')
    show_cart(message, edit_message=True)


@bot.callback_query_handler(lambda call: 'order' in call.data)
def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id

    _, cart_id = call.data.split('_')
    cart_id = int(cart_id)

    time_now = datetime.now().strftime('%H:%M')
    new_date = datetime.now().strftime('%d.%m.%Y')

    cart_product = get_cart_products(cart_id)
    total_products, total_price = get_total_products_price(cart_id)

    save_order_total(cart_id, total_products, total_price, time_now, new_date)
    order_total_id = orders_total_price_id(cart_id)

    text = 'Ваша корзина \n\n'
    i = 0
    for product_name, quantity, final_price in cart_product:
        i += 1
        text += f'''{i}. {product_name}
    Количество: {quantity}
    Общая стоимость: {final_price}\n\n'''

        save_order(order_total_id, product_name, quantity, final_price)

    text += f'''Общее количество продуктов: {0 if total_products is None else total_products}  
    Общая стоимость счета: {0 if total_price is None else total_price}'''

    bot.send_invoice(
        chat_id=chat_id,
        title=f'Заказ №{cart_id}',
        description=text,
        invoice_payload='bot-defined invoice payload',
        provider_token='398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065',
        currency='UZS',
        prices=[
            LabeledPrice(label='общая стоимость', amount=int(total_price * 100)),
            LabeledPrice(label='Доставка', amount=1000000)
        ],
        start_parameter='start_parameter'
    )

@bot.pre_checkout_query_handler(lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message='Ошибка оплата не прошла')


@bot.message_handler(content_types=['successful_payment'])
def get_payment(message: Message):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    bot.send_message(chat_id, 'Ваша оплата прошла успешно . Ожидайте свой заказ')
    drop_cart_products_default(cart_id)


@bot.message_handler(regexp='История')
def show_history_orders(message: Message):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    orders_total_price = get_order_total_price(cart_id)

    for i in orders_total_price:
        text = f'''Дата заказа {i[-1]}
Время заказа {i[-2]}
Общее количество {i[3]}
Сумма счёта: {i[2]}\n\n'''
        detail_product = get_detail_product(i[0])
        for j in detail_product:
            text += f'''Продукт: {j[0]}
Количество: {j[1]}
Общая стоимость {j[2]}\n\n'''
        bot.send_message(chat_id, text)


# @bot.message_handler(content_types=['photo'])
# def handle_photo(message):
#     chat_id = message.chat.id
#     id_photo = message.photo[0].file_id
#     print(id_photo)
#     bot.send_photo(message.chat.id, id_photo)


bot.infinity_polling()
