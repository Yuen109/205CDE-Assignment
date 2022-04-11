from flask import Flask, redirect, url_for, render_template, request, session, flash
import pymysql

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = 'the random string'  

# Connect to the database
db = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             database='booking',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# home page
@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form.get('action1') == 'Looking for more?':
            render_template("hotel.html") 
        elif  request.form.get('action2') == 'Looking for more?':
            render_template("guide.html") 
        else:
            request.form.get('action3') == 'Looking for more?'
            render_template("car.html") 

    return render_template("index.html")

# hotel page  
@app.route("/hotel", methods=['GET', 'POST'])
def hotel():
    db.ping(reconnect=True)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM products where product_type = "Hotel Room"')
    post = cursor.fetchall()

    for row in post:
        product_id = list(row.values())[0]
        session['product_id'] = product_id
        # print(session['product_id'])
        
    return render_template("hotel.html", post = post, product_id = product_id)

# tour guide page
@app.route("/guide", methods=['GET', 'POST'])
def guide():
    db.ping(reconnect=True)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM products where product_type = "Tour Guide"')
    post = cursor.fetchall()
    for row in post:
        product_id = list(row.values())[0]
        session['product_id'] = product_id
    return render_template("guide.html", post = post, product_id = product_id)

# vehicle page
@app.route("/car", methods=['GET', 'POST'])
def car():
    db.ping(reconnect=True)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM products where product_type = "Car"')
    post = cursor.fetchall()
    for row in post:
        product_id = list(row.values())[0]
        session['product_id'] = product_id
    return render_template("car.html", post = post, product_id = product_id)

# question for imorovement
@app.route("/question", methods=['GET', 'POST'])
def question():
    if request.method == 'POST':
        question = request.form.get('ansQuestion')

        if len(question) < 1:
            flash('Area cannot be empty!', category='error')
        else:
            cursor = db.cursor()
            cursor.execute('INSERT INTO question (question) VALUE (%s)', (question))

            try:
                db.commit()
                flash('Successfully inserted Thank You')
            except:
                db.rollback()
            
            db.close()
    return render_template("question.html")

# pruchase item
@app.route("/purchase/<int:product_id>", methods=['GET', 'POST'])
def purchase(product_id):
    db.ping(reconnect=True)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE product_id = %s', (session['product_id']))
    pay = cursor.fetchall()
    for row in pay:
        product_id = list(row.values())[0]
        session['product_id'] = product_id
        product_id = session['product_id']

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        date = request.form.get('date')
        article = request.form.get('article')
        author = request.form.get('author')
        price = request.form.get('price')
        customer_id = request.form.get('customer_id')        

        cursor = db.cursor()
        cursor.execute('INSERT INTO order_details (product_id, date, article, author, price, customer_id) VALUE (%s, %s, %s, %s, %s, %s)', 
            (product_id, date, article, author, price, customer_id)) 
        
        try:              
            db.commit()
            flash('purchase Scuuessfully')
            return redirect(url_for('payment'))
        except:
            db.rollback()
            flash('purchase Fail', category='error')
        db.close()
        
    return render_template("purchase.html", pay = pay, product_id = product_id)

# pay for item
@app.route("/payment", methods=['GET', 'POST'])
def payment():
    db.ping(reconnect=True)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM order_details')
    order = cursor.fetchall()

    if request.method == 'POST':
        name = request.form.get('firstName')
        startDay = request.form.get('startDay')
        endDay = request.form.get('endDay')
        price = request.form.get('price')
        detail_id = request.form.get('detail_id')

        cursor = db.cursor()
        cursor.execute('INSERT INTO payment (start_day, end_day, price, detail_id) VALUES (%s, %s, %s, %s)', 
            (startDay, endDay, price, detail_id))
        profile = cursor.fetchone()

        try:
            db.commit()
            print("Successfully inserted")
            flash('Payment Success')
            return redirect(url_for('home'))
        except:
            flash('Payment Fail')
            db.rollback()
        db.close()
    return render_template("payment.html", session = session, order = order)

@app.route("/login/profile/updateUser/", methods=['GET', 'POST'])
def updateUser():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be grater than 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be grater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Password don\'s match.', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters.', category='error')
        else:
            cursor = db.cursor()
            cursor.execute('UPDATE customers SET name = %s, email = %s, password1 = %s, password2 = %s WHERE customer_id = %s', 
                (firstName, email, password1, password2, session['id']))
            profile = cursor.fetchone()
            try:
                db.commit()
                print("Successfully updated")
                flash('Update successfully')
                return redirect(url_for('profile'))
            except:
                db.rollback()
            
            db.close()
            flash('Update successfully', category='success', session = session, profile = profile) 

    return render_template("updateUser.html", session = session)

@app.route("/login/profile/updateProduct/", methods=['GET', 'POST'])
def updateProduct():
    if request.method == 'POST':
        user_id = request.form.get('id')
        firstName = request.form.get('firstName')
        title = request.form.get('title')
        price = request.form.get('price')
        product_id = request.form.get('product_id')
        img = request.form.get('img')
        

        if len(firstName) == session['firstName']:
            flash('Your name is not correct!', category='error')
        elif len(title) < 2:
            flash('Enter a better title.', category='error')
        else:
            cursor = db.cursor()
            cursor.execute('UPDATE products SET customer_id = %s, user_name = %s, title = %s, price = %s, img = %s WHERE product_id = %s', 
                (user_id, firstName, title, price, img, product_id))
            update = cursor.fetchall()

            try:              
                db.commit()
                flash('Upload scuuessfully')
                return redirect(url_for('profile'))
            except:
                db.rollback()
            db.close()
            # flash('Account created.', category='success')
    return render_template("updateProduct.html", session = session)

@app.route("/login/profile/deleteProduct", methods=['GET', 'POST'])
def deleteProduct():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        cursor = db.cursor()
        # product_id = cursor.execute('SELECT product_id FROM products')
        # product_id = cursor.fetchall()
        cursor.execute('DELETE FROM products WHERE product_id = %s)', (product_id))
        delete = cursor.fetchone() 
 
        try:
            db.commit()
            flash('Your post has been delete')
            return redirect(url_for('profile'))
        except:
            flash('Cannot delete')
            db.rollback()
        db.close()
    return render_template("deleteProduct.html", session = session)

#upload product to database 
@app.route("/login/upload/", methods=['GET', 'Post'])
def upload():  
    if request.method == 'POST':
        user_id = request.form.get('id')
        firstName = request.form.get('firstName')
        title = request.form.get('title')
        group = request.form.get('group')
        price = request.form.get('price')
        img = request.form.get('img')

        if len(firstName) == session['firstName']:
            flash('Your name is not correct!', category='error')
        elif len(title) < 2:
            flash('Enter a better title.', category='error')
        elif group == '':
            flash('Choose a type.', category='error')
        else:
            cursor = db.cursor()
            cursor.execute('INSERT INTO products (customer_id, user_name, title, product_type, price, img) VALUES (%s, %s, %s, %s, %s, %s)', 
                (user_id, firstName, title, group, price, img))
            profile = cursor.fetchone()      

            try:
                db.commit()
                print("Successfully inserted")
                flash('Upload scuuessfully')
                return redirect(url_for('profile'))
            except:
                db.rollback()
            db.close()
            # flash('Account created.', category='success')
    return render_template('upload.html', session = session)

# this will be the profile page, only accessible for loggedin users
@app.route('/login/profile/', methods=['GET', 'Post'])
def profile():
    db.ping(reconnect=True)
    # Check if user is loggedin
    if 'loggedin' in session:
    #     We need all the account info for the user so we can display it on the profile page
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM customers WHERE customer_id = %s', (session['id']))
        account = cursor.fetchone()

    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM products WHERE user_name = %s AND customer_id = %s', (session['firstName'], session['id']))
        profile = cursor.fetchall()

        # Show the profile page with account info
    return render_template('profile.html', account = account, profile = profile)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    db.ping(reconnect=True)
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'firstName' in request.form and 'password1' in request.form:
        # Create variables for easy access
        firstName = request.form['firstName']
        password1 = request.form['password1']
        # Check if account exists using MySQL
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM customers WHERE name = %s AND password1 = %s', (firstName, password1,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['customer_id']
            session['firstName'] = account['name']
            session['email'] = account['email']
            session['password1'] = account['password1']
            session['password2'] = account['password2']
            return redirect(url_for('profile'))

        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password!', category='error')
            # msg = 'Incorrect username/password!'
    return render_template('login.html')

@app.route("/signUp/", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be grater than 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be grater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Password don\'s match.', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters.', category='error')
        else:
            cursor = db.cursor()
            cursor.execute('INSERT INTO customers (name, email, password1, password2) VALUES (%s, %s, %s, %s)', (firstName, email, password1, password2))

            try:
                db.commit()
                print("Successfully inserted")
                flash('Create successfully')
                return redirect(url_for('login'))
            except:
                db.rollback()
            
            db.close()
            flash('Account created.', category='success')    
    # return redirect(url_for('userInfo', name = user))
    return render_template("signUp.html")

@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   flash('You logout successfully!')
   # Redirect to login page
   return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)