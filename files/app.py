from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import math

app = Flask(__name__)

DATABASE = 'items.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                itemName TEXT NOT NULL,
                itemCode TEXT NOT NULL,
                date TEXT NOT NULL,
                batchNo TEXT NOT NULL,
                price REAL NOT NULL
            );
        ''')

create_table()

def get_next_item_code():
    with get_db_connection() as conn:
        result = conn.execute('SELECT COUNT(*) AS count FROM Item').fetchone()
        count = result['count']
        next_code = f'TTPL/{count + 1:03d}'
        return next_code

@app.route('/')
def index():
    conn = get_db_connection()

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Count total items
    total_items = conn.execute('SELECT COUNT(*) AS count FROM Item').fetchone()['count']

    # Calculate total pages
    total_pages = math.ceil(total_items / limit) if limit > 0 else 1

    # Adjust page number if out of bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    # Calculate offset for SQL query
    offset = (page - 1) * limit

    # Fetch items for the current page
    if limit > 0:
        items = conn.execute('SELECT * FROM Item ORDER BY id DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
    else:
        items = conn.execute('SELECT * FROM Item ORDER BY id DESC').fetchall()

    next_item_code = get_next_item_code()
    conn.close()

    return render_template('index.html', items=items, next_item_code=next_item_code, page=page, limit=limit, total_pages=total_pages)

@app.route('/add', methods=['POST'])
def add_item():
    item_data = {
        'itemName': request.form['itemName'],
        'itemCode': request.form['itemCode'],
        'date': request.form['date'],
        'batchNo': request.form['batchNo'],
        'price': float(request.form['price'])
    }
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO Item (itemName, itemCode, date, batchNo, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_data['itemName'], item_data['itemCode'], item_data['date'], item_data['batchNo'], item_data['price']))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    item_data = {
        'itemName': request.form['itemName'],
        'itemCode': request.form['itemCode'],
        'date': request.form['date'],
        'batchNo': request.form['batchNo'],
        'price': float(request.form['price'])
    }
    with get_db_connection() as conn:
        conn.execute('''
            UPDATE Item
            SET itemName = ?, itemCode = ?, date = ?, batchNo = ?, price = ?
            WHERE id = ?
        ''', (
            item_data['itemName'],
            item_data['itemCode'],
            item_data['date'],
            item_data['batchNo'],
            item_data['price'],
            item_id
        ))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM Item WHERE id = ?', (item_id,))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
