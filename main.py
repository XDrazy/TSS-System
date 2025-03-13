import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="hongqirong233",  # 替换为你的实际密码
        database="tss_db",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS destinations (
                code VARCHAR(3) PRIMARY KEY,
                name VARCHAR(50),
                price DECIMAL(10,2),
                stock INT
            )
        ''')
        
        cursor.execute("SHOW COLUMNS FROM destinations LIKE 'stock'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE destinations ADD COLUMN stock INT")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                destination_code VARCHAR(3),
                ticket_type VARCHAR(20),
                seat_type VARCHAR(20),
                price DECIMAL(10,2),
                purchase_time DATETIME,
                payment_method VARCHAR(20),
                status VARCHAR(20)
            )
        ''')
        
        cursor.execute("SHOW COLUMNS FROM tickets LIKE 'status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE tickets ADD COLUMN status VARCHAR(20)")
        
        cursor.execute('TRUNCATE TABLE destinations')
        cursor.execute('''
            INSERT INTO destinations (code, name, price, stock) VALUES
            ('2U0', '总站', 10.00, 50),
            ('3K1', '南站', 8.50, 30),
            ('4M2', '东站', 12.00, 20)
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise

class TicketSellSys:
    def __init__(self):
        self.destinations = {}
        self.ticket_types = ['单程票', '多次往返票']
        self.seat_types = ['普通座', '舒适座']
        self.load_destinations()

    def load_destinations(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT code, name, price, stock FROM destinations")
        for row in cursor.fetchall():
            self.destinations[row['code']] = {
                'name': row['name'], 
                'price': float(row['price']), 
                'stock': row['stock']
            }
        cursor.close()
        conn.close()

    def calculate_price(self, dest_code, ticket_type, seat_type):
        base_price = self.destinations[dest_code]['price']
        return base_price * (1.5 if ticket_type == '多次往返票' else 1) * \
               (1.2 if seat_type == '舒适座' else 1)

    def save_ticket(self, dest_code, ticket_type, seat_type, price, payment_method):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tickets (destination_code, ticket_type, seat_type, price, purchase_time, payment_method, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (dest_code, ticket_type, seat_type, price, datetime.now(), payment_method, '已支付'))
            cursor.execute('UPDATE destinations SET stock = stock - 1 WHERE code = %s', (dest_code,))
            conn.commit()
            cursor.close()
            conn.close()
            # 重新加载 destinations 以更新库存
            self.load_destinations()
        except Exception as e:
            print(f"保存票务失败: {e}")
            conn.rollback()
            raise

tss = TicketSellSys()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start':
            session.clear()
            return redirect(url_for('select_destination'))
        elif action == 'reset':
            flash('系统已重置', 'success')
            session.clear()
    return render_template('index.html')

@app.route('/select_destination', methods=['GET', 'POST'])
def select_destination():
    if request.method == 'POST':
        dest_code = request.form['destination'].upper()
        if dest_code in tss.destinations and tss.destinations[dest_code]['stock'] > 0:
            session['dest_code'] = dest_code
            return redirect(url_for('select_options'))
        flash('无效的目的地代码或库存不足', 'danger')
    return render_template('select_destination.html', destinations=tss.destinations)

@app.route('/select_options', methods=['GET', 'POST'])
def select_options():
    if 'dest_code' not in session:
        flash('请先选择目的地', 'warning')
        return redirect(url_for('select_destination'))
    if request.method == 'POST':
        ticket_type = request.form['ticket_type']
        seat_type = request.form['seat_type']
        price = tss.calculate_price(session['dest_code'], ticket_type, seat_type)
        session['ticket_type'] = ticket_type
        session['seat_type'] = seat_type
        session['ticket_type'] = ticket_type
        session['seat_type'] = seat_type
        session['price'] = price
        return redirect(url_for('payment'))
    return render_template('select_options.html', ticket_types=tss.ticket_types, 
                         seat_types=tss.seat_types, dest_name=tss.destinations[session['dest_code']]['name'])

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    required_keys = ['dest_code', 'ticket_type', 'seat_type', 'price']
    if not all(k in session for k in required_keys):
        flash('购票流程出错，请重新开始', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        try:
            tss.save_ticket(session['dest_code'], session['ticket_type'], 
                           session['seat_type'], session['price'], payment_method)
            return redirect(url_for('print_ticket'))
        except Exception as e:
            flash('购票失败，请重试', 'danger')
            return redirect(url_for('payment'))
    return render_template('payment.html', price=session['price'], 
                         dest_name=tss.destinations[session['dest_code']]['name'],
                         ticket_type=session['ticket_type'], seat_type=session['seat_type'])

@app.route('/print_ticket')
def print_ticket():
    required_keys = ['dest_code', 'ticket_type', 'seat_type', 'price']
    if not all(k in session for k in required_keys):
        flash('购票流程出错，请重新开始', 'danger')
        return redirect(url_for('index'))
    ticket_info = {
        'destination': tss.destinations[session['dest_code']]['name'],
        'ticket_type': session['ticket_type'],
        'seat_type': session['seat_type'],
        'price': session['price'],
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ticket_id': random.randint(100000, 999999)
    }
    return render_template('print_ticket.html', ticket=ticket_info)

@app.route('/set_language/<lang>')
def set_language(lang):
    session['language'] = lang
    flash(f'语言已切换为{"中文" if lang == "zh" else "English"}', 'success')
    return redirect(request.referrer or url_for('index'))

if __name__ == "__main__":
    init_database()
    tss = TicketSellSys()
    app.run(debug=True)