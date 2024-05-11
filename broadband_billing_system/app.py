import datetime
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector as mycon

app = Flask(__name__)

# Configure MySQL connection
db = mycon.connect(
    host="localhost",
    user="root",
    password="fg3*d12",
    database="DBMS"
)

def create_tables():
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customer (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            mobile_number VARCHAR(20),
            address TEXT,
            type VARCHAR(30),
            id_proof VARCHAR(50)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subscription (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cost DECIMAL(10, 2),
            details TEXT,
            speed VARCHAR(20)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BillDetail (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            subscription_id INT,
            month VARCHAR(20),
            cost DECIMAL(10, 2),
            status VARCHAR(20),
            FOREIGN KEY (customer_id) REFERENCES Customer(id),
            FOREIGN KEY (subscription_id) REFERENCES Subscription(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TransactionDetail (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bill_id INT,
            date_of_payment DATE,
            paid_amount DECIMAL(10, 2),
            pay_method VARCHAR(20),
            FOREIGN KEY (bill_id) REFERENCES BillDetail(id)
        )
    """)
    cursor.close()

# Check and create tables when the application starts
create_tables()

# Define SQLAlchemy models
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Customer:
    def __init__(self, id, name, mobile_number, address,customer_type,id_proof):
        self.id = id
        self.name = name
        self.mobile_number = mobile_number
        self.address = address
        self.customer_type = customer_type
        self.id_proof = id_proof

class Subscription:
    def __init__(self, id, customer_id, cost, details, speed):
        self.id = id        
        self.cost = cost
        self.details = details
        self.speed = speed

class BillDetail:
    def __init__(self, id, customer_id, subscription_id, month, cost, status):
        self.id = id
        self.customer_id = customer_id
        self.subscription_id = subscription_id
        self.month = month
        self.cost = cost
        self.status = status

class TransactionDetail:
    def __init__(self, id, bill_id, date_of_issue, paid_amount, pay_method):
        self.id = id
        self.bill_id = bill_id
        self.date_of_issue = date_of_issue
        self.paid_amount = paid_amount
        self.pay_method = pay_method

# Dummy users for demonstration purposes
users = [
    User(id=1, username="RA2111029010020", password="sob")
]

# Define routes
@app.route('/')
def index():
    # Check if user is logged in (authenticated)
    if "username" in session and session["username"] == "RA2111029010020":
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the entered username and password match predefined credentials
        if any(user.username == username and user.password == password for user in users):
            # Store username in session to indicate user is logged in
            session["username"] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)
    else:
        # If GET request, render login page
        return render_template('login.html', error=None)



@app.route('/add_details', methods=['POST','GET'])
def add_details():
    # Retrieve form data

    if request.method=='GET':
        return render_template('add_details.html')
    
    type = request.form.get('type')
    if type == 'customer':
        return render_template('add_customer.html')
    elif type == 'subscription':
         return render_template('add_subscription.html')
    else:
        # Handle invalid form data
        return render_template('error.html', message='Invalid form data')
    
@app.route('/add_customer', methods=['POST','GET'])
def add_customer():
    # Retrieve form data

    if request.method=='POST':
        name = request.form.get('name')
        mobile_number = request.form.get('mobile_number')
        address = request.form.get('address')
        customer_type = request.form.get('customer_type')
        customer_id_proof = request.form.get('customer_id_proof')
        # Insert customer details into the database
        cursor = db.cursor()
        cursor.execute("INSERT INTO Customer (name, mobile_number, address,type,id_proof) VALUES (%s, %s, %s, %s, %s)", (name, mobile_number, address,customer_type,customer_id_proof))
        db.commit()
        cursor.close()
        return render_template('success.html')
    elif request.method=='GET':
        return render_template('add_customer.html')

    
@app.route('/add_subscription', methods=['POST','GET'])
def add_subscription():
    # Retrieve form data

    if request.method=='POST':
        if "username" in session:    
            subscription_cost = request.form.get('subscription_cost')
            subscription_details = request.form.get('subscription_details')
            subscription_speed = request.form.get('subscription_speed')
            # Insert customer details into the database
            cursor = db.cursor()
            cursor.execute("INSERT INTO Subscription ( cost, details, speed) VALUES ( %s, %s, %s)", (subscription_cost, subscription_details, subscription_speed))
            db.commit()
            cursor.close()
            return render_template('success.html')
    elif request.method=='GET':
        return render_template('add_subscription.html')
    


@app.route('/customer_details')
def customer_details():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Customer")
    customers = cursor.fetchall()
    print(customers)
    cursor.close()
    return render_template('customer_details.html', customers=customers)

@app.route('/billing')
def billing_info():
    return render_template('add_bill.html')

@app.route('/submit_billing_data', methods=['GET', 'POST'])
def submit_billing_data():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        subscription_id = request.form.get('subscription_id')
        month = request.form.get('month')

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer WHERE id = %s",(customer_id,))
        customer_exist= True if len(cursor.fetchall())>0 else False

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Subscription WHERE id = %s",(subscription_id,))
        subscription_fetched=cursor.fetchall()
        
        subscription_exist= True if len(subscription_fetched)>0 else False
        cursor.close()

        if(customer_exist and subscription_exist):
            cursor = db.cursor()
            cursor.execute("INSERT INTO BillDetail ( customer_id, subscription_id, month, cost, status) VALUES ( %s, %s, %s, %s, %s)", (customer_id, subscription_id, month, subscription_fetched[0]['cost'],"UNPAID"))
            db.commit()
            cursor.close()
            return render_template('success.html')
        return render_template('failed.html')
    else:
        # If GET request, render the billing info page
        return render_template('add_bill.html')
    

@app.route('/pay_bill', methods=['GET', 'POST'])
def pay_bill():
    if request.method == 'POST':
        bill_number = request.form.get('bill_number')
        payment_method = request.form.get('payment_method')
        

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM BillDetail WHERE id = %s",(bill_number,))
        bill_fetched=cursor.fetchall()
        bill_exist= True if len(bill_fetched)>0 else False
        cursor.close()

        if(bill_exist and bill_fetched[0]['status']=="UNPAID"):
            current_date= datetime.datetime.today().strftime('%Y-%m-%d')
            cursor = db.cursor()
            cursor.execute("INSERT INTO TransactionDetail ( bill_id, date_of_payment, paid_amount, pay_method) VALUES ( %s, %s, %s, %s)", (bill_number, current_date, bill_fetched[0]['cost'], payment_method))
            db.commit()
            cursor.close()
            cursor = db.cursor()
            cursor.execute("UPDATE BillDetail SET status = %s WHERE id = %s", ("PAID",bill_number))
            db.commit()
            cursor.close()
            return render_template('success.html')
        return render_template('failed.html')
    else:
        # If GET request, render the billing info page
        return render_template('billing_payment.html')

@app.route('/subscription_details')
def subscription_details():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Subscription")
    subscriptions = cursor.fetchall()
    print(subscriptions)
    cursor.close()
    return render_template('subscription_details.html', subscriptions=subscriptions)

@app.route('/bills_details')
def bills_details():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM BillDetail")
    bills = cursor.fetchall()
    cursor.close()
    print(bills)
    return render_template('bills_details.html', bills=bills)

@app.route('/transaction_details')
def transaction_details():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM TransactionDetail")
    transactions = cursor.fetchall()
    cursor.close()
    return render_template('transaction_details.html', transactions=transactions)

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
