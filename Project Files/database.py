import sqlite3 

DATABASE = "shopmind.db"

def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')

    # orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    connection.commit()

    # Add sample products if database is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]

    if product_count == 0:
        products = [
            (
                "NovaBook Pro",
                "Laptop",
                69999,
                "High-performance laptop with 16GB RAM and 512GB SSD.",
                10
            ),
            (
                "NovaBook Air",
                "Laptop",
                49999,
                "Lightweight laptop for students and professionals.",
                15
            ),
            (
                "PixelSound Pro",
                "Headphones",
                7999,
                "Wireless noise-cancelling headphones.",
                25
            ),
            (
                "GameCore X",
                "Gaming",
                89999,
                "Gaming desktop with powerful GPU and 32GB RAM.",
                5
            ),
            (
                "FitWatch 3",
                "Smartwatch",
                5999,
                "Smartwatch with fitness tracking.",
                20
            )
        ]

        cursor.executemany('''
            INSERT INTO products (name, category, price, description, stock)
            VALUES (?, ?, ?, ?, ?)
        ''', products)
        connection.commit()
        connection.close()
        
def get_products():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    connection.close()
    return [dict(product) for product in products]

def get_product(product_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    connection.close()
    if product:
        return dict(product)
    return None

def create_order(customer_name, product_id, quantity):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Get product using the same database connection
        cursor.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            raise ValueError("Product not found")

        if product["stock"] < quantity:
            raise ValueError("Not enough stock available")

        total = product["price"] * quantity

        # Create order
        cursor.execute("""
            INSERT INTO orders
            (customer_name, product_id, quantity, total)
            VALUES (?, ?, ?, ?)
        """, (
            customer_name,
            product_id,
            quantity,
            total
        ))

        # Reduce stock
        cursor.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE id = ?
        """, (
            quantity,
            product_id
        ))

        # Save transaction
        connection.commit()

        order_id = cursor.lastrowid

        return {
            "order_id": order_id,
            "total": total
        }

    except Exception:

        # Undo changes if anything fails
        connection.rollback()

        raise

    finally:

        # Always close the connection
        connection.close()

    return {
        "order_id": order_id,
        "customer_name": customer_name,
        "product_id": product_id,
        "quantity": quantity,
        "total": total
    }