import sqlite3


def create_table_users():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        user_name TEXT,
        phone TEXT,
        admin VARCHAR(30)
        );''')


def create_table_carts():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS carts(
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(user_id),
        total_price DECIMAL(12, 2) DEFAULT 0,
        total_products INTEGER DEFAULT 0 
        );''')


def create_cart_products_table():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS cart_products(
        cart_product_Id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name VARCHAR(50) NOT NULL,
        quantity INTEGER NOT NULL,
        final_price DECIMAL(12, 2) NOT NULL,
        cart_id INTEGER REFERENCES cart(cart_id),

        UNIQUE(product_name, cart_id)
    );''')


def create_categories_table():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(30) NOT NULL UNIQUE
    );''')


def insert_categories(category_name):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO categories(category_name) VALUES (?)
    ''', (category_name,))
    conn.commit()
    conn.close()


def create_products_table():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS products(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(30) NOT NULL UNIQUE,
    price DECIMAL(12, 2) NOT NULL,
    description VARCHAR(200),
    image TEXT,
    category_id INTEGER NOT NULL,

    FOREIGN KEY(category_id) REFERENCES categories(category_id)
    );''')


# def create_products_photo():
#     conn = sqlite3.connect('users.db')
#     cur = conn.cursor()
#
#     cur.execute('''CREATE TABLE IF NOT EXISTS photo_carts(
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     photo_artikul VARCHAR(30),
#     photo_1 VARCHAR(255),
#     photo_2 VARCHAR(255),
#     photo_3 VARCHAR(255),
#     photo_4 VARCHAR(255),
#     photo_5 VARCHAR(255),
#     photo_6 VARCHAR(255),
#     photo_7 VARCHAR(255),
#     photo_8 VARCHAR(255),
#     photo_9 VARCHAR(255),
#     photo_10 VARCHAR(255),
#
#
#     FOREIGN KEY(photo_artikul) REFERENCES products(product_id)
#     );''')


def insert_product_table(product_name, price, description, image, category_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO products(product_name, price, description, image, category_id) VALUES
    (?, ?, ?, ?, ?)''', (product_name, price, description, image, category_id))
    conn.commit()
    conn.close()



def first_select_user(chat_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT * FROM users WHERE telegram_id = ?
    ''', (chat_id,))
    user = cur.fetchone()
    conn.close()
    return user


def first_select_admin(chat_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT admin, telegram_id FROM users
    WHERE telegram_id = ?
    ''', (chat_id,))
    user = cur.fetchone()
    conn.close()
    return user


def first_register_admin(chat_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    UPDATE users
        SET admin = ?
        WHERE telegram_id = ?
    ''', ('Yes', chat_id))
    conn.commit()
    conn.close()


def first_register_user(chat_id, full_name):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO users(telegram_id, user_name) VALUES (?, ?)
    ''', (chat_id, full_name))
    conn.commit()
    conn.close()


def update_user_finish_register(phone, chat_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    UPDATE users
        SET phone = ?
        WHERE telegram_id = ?
    ''', (phone, chat_id))
    conn.commit()
    conn.close()


def insert_to_cart(chat_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO carts(user_id) VALUES 
    (
    (SELECT user_id FROM users WHERE telegram_id = ?)
    );
    ''', (chat_id,))
    conn.commit()
    conn.close()


def get_all_categories():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT * FROM categories;
    ''')
    categories = cur.fetchall()
    conn.close()
    return categories


def get_products_by_category_id(category_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT product_id, product_name FROM products
    WHERE category_id = ?
    ''', (category_id,))
    products = cur.fetchall()
    conn.close()
    return products


def get_product_detail(product_id: object) -> object:
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT * FROM products
    WHERE product_id = ?
    ''', (product_id,))
    products = cur.fetchone()
    conn.close()
    return products


def get_user_cart_id(chat_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''
    SELECT cart_id FROM carts
    WHERE user_id = (
        SELECT user_id FROM users WHERE telegram_id = ?
    )
    ''', (chat_id,))
    cart_id = cur.fetchone()[0]
    conn.close()
    return cart_id


def get_quantity(cart_id, product):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('''
    SELECT quantity FROM cart_products
    WHERE cart_id = ? AND product_name = ?
    ''', (cart_id, product))
    quantity = cur.fetchone()[0]
    conn.close()
    return quantity


def insert_or_update_cart_product(cart_id, product_name, quantity, final_price):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
            VALUES(?, ?, ?, ?)
            ''', (cart_id, product_name, quantity, final_price))
        conn.commit()
        return True
    except:
        cur.execute('''
        UPDATE cart_products
        SET quantity = ?,
        final_price = ?
        WHERE product_name = ? AND cart_id = ?
        ''', (quantity, final_price, product_name, cart_id))
        conn.commit()
        return False
    finally:
        conn.close()


def update_total_product_total_price(cart_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    UPDATE carts
    SET total_products = (
    SELECT SUM(quantity) FROM cart_products
    WHERE cart_id = :cart_id
    ),
    total_price = (
    SELECT SUM(final_price) FROM cart_products
    WHERE cart_id = :cart_id
    )
    WHERE cart_id = :cart_id
    ''', {'cart_id': cart_id})
    conn.commit()
    conn.close()


def get_cart_products(cart_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT product_name, quantity, final_price
    FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cur.fetchall()
    conn.close()
    return cart_products


def get_total_products_price(cart_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT total_products, total_price FROM carts 
    WHERE cart_id = ?
    ''', (cart_id,))
    total_products, total_price = cur.fetchone()
    conn.close()
    return total_products, total_price


def get_carts_products_for_delete(cart_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT cart_product_id, product_name FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cur.fetchall()
    conn.close()
    return cart_products


def delete_cart_products_from(cart_product_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    DELETE FROM cart_products 
    WHERE cart_product_id = ?
    ''', (cart_product_id,))
    conn.commit()
    conn.close()


def drop_cart_products_default(cart_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    DELETE FROM cart_products 
    WHERE cart_id = ?
    ''', (cart_id,))
    conn.commit()
    conn.close()


def orders_total_price():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS orders_total_price(
    order_total_price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER REFERENCES carts(cart_id),
    total_price DECIMAL(12, 2) DEFAULT 0,
    total_products INTEGER DEFAULT 0,
    time_now TEXT,
    new_date TEXT
    );
    ''')


def order():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS orders(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_total_price_id INTEGER REFERENCES orders_total_price(orders_total_price_id),
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    final_price DECIMAL(12, 2) NOT NULL
    );
    ''')


def save_order_total(cart_id, total_products, total_price, time_now, new_date):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO orders_total_price(cart_id, total_products, total_price, time_now, new_date)
    VALUES(?, ?, ?, ?, ?)
    ''', (cart_id, total_products, total_price, time_now, new_date))
    conn.commit()
    conn.close()


def orders_total_price_id(cart_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT order_total_price_id FROM orders_total_price
    WHERE cart_id = ?
    ''', (cart_id,))
    order_total_id = cur.fetchall()[-1][0]
    conn.close()
    return order_total_id


def save_order(order_total_id, product_name, quantity, final_price):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO orders(order_total_price_id, product_name, quantity, final_price)
    VALUES(?, ?, ?, ?)
    ''', (order_total_id, product_name, quantity, final_price))
    conn.commit()
    conn.close()


def get_order_total_price(cart_id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT * FROM orders_total_price
    WHERE cart_id = ?
    ''', (cart_id,))
    orders_total_price = cur.fetchall()
    conn.close()
    return orders_total_price


def get_detail_product(id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('''
    SELECT product_name, quantity, final_price FROM orders
    WHERE order_total_price_id = ?
    ''', (id,))
    detail_product = cur.fetchall()
    conn.close()
    return detail_product
