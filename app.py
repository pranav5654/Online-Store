from flask import Flask, render_template, request, redirect, url_for , session
import mysql.connector

from datetime import datetime

# logout ----> done

#order history ------> done

# proflie update -----> done

# back option in cart page


order_id = 1








app = Flask(__name__)
app.secret_key = "new"

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="FDSAfdsaa1.",
    database="megamartonline"
)

c = conn.cursor()

#change to -1

id = -1

@app.route('/')
def index():

    return render_template('index.html')

    # return render_template('dashboard.html')



@app.route('/login_page')
def login_page():
    return render_template('login.html')




@app.route('/log_out')
def log_out():
    global id
    id = -1
    return render_template('login.html')



@app.route('/register' , methods = ['POST'])
def register():
    try:
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        dob = request.form['dob']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        c.execute("select consumer_id from  consumer order by consumer_id desc")
        c_id = c.fetchall()[0][0] + 1
        
        query = "insert into consumer values(%s,%s,%s,%s,%s,%s,%s,%s)"
        c.execute(query , (c_id , c_id , name , dob , email , 0 , phone_number ,address))
        conn.commit()

        query = "insert into cart values(%s,%s)"
        c.execute(query , (c_id , c_id))
        conn.commit()

        query = "insert into consumer_login values(%s,%s,%s)"
        c.execute(query , (c_id , username , password))
        conn.commit()
    except Exception as e:
        conn.rollback()

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    global id
    username = request.form['username']
    password = request.form['password']


    query = "SELECT * FROM consumer_login WHERE username = %s AND password = %s"
    c.execute(query, (username, password))
    id = c.fetchall()


    if(len(id)   != 0):
        
        id = id[0][0]
        session[username]  = username
        return redirect(url_for('dashboard'))
    
    else:
        return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():

    if id == -1 :
        return render_template('login.html')

    products = c.execute("select category , Specific_name , Price , Description  , Product_id from product ")
    products = c.fetchall()


    return render_template('dashboard.html' , products = products)


@app.route('/orders')
def orders():
    global id
    if id == -1 :
        return render_template('login.html')

    query = "select o.product_id , o.dop  from orders o  where o.consumer_id = %s "

    products = c.execute(query , [id])
    products = c.fetchall()

    print(products)


    return render_template('history.html' , products = products)






@app.route('/cart')
def cart():
    global id

    query = " select product_id from cart_products where cart_id = %s"
    c.execute(query , [id] )
    product_id = c.fetchall()
    products = []

    for i in product_id:
        query = " select Specific_name , Price from product where Product_id = %s"
        c.execute(query , [ i[0] ] )
        a = c.fetchall()
        products.append(a[0])


    return render_template("cart.html" , products = products)



@app.route('/checkout')
def checkout():
    global id , order_id

    query = " select product_id from cart_products where cart_id = %s"
    c.execute(query , [id] )
    product_id = c.fetchall()

    try:

        for i in product_id:
            query = " delete from product where  Product_id = %s"
            c.execute(query  , [ i[0] ])
            conn.commit()
            query = " delete from cart_products where  product_id = %s"
            c.execute(query  , [ i[0] ])
            conn.commit()

            query = " insert into orders values(%s,%s,%s,%s)"

            c.execute(query  , [ order_id , datetime.now().date() ,  i[0] , id ] )
            order_id += 1
            conn.commit()

    except Exception as e:
        conn.rollback()


    return redirect(url_for('dashboard'))


@app.route('/add', methods=['POST'])
def add():
    global id
    try:
        p_id = request.json.get('id')
        query = " INSERT INTO cart_products (cart_id, product_id) VALUES(%s , %s)"
        c.execute(query , (id , p_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
    return redirect(url_for('dashboard'))
    


@app.route('/profile_update' , methods=['GET']) 
def profile_update_get():
    global id

    query = " select * from consumer where consumer_id = %s"
    profile = c.execute(query , [id])
    profile = c.fetchall()

    profile = profile[0]
    return render_template("profile.html" , profile = profile)


# transaction
@app.route('/profile_update' , methods=['POST']) 
def profile_update():
    global id

    try:
        name = request.form['name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']


        query = "update consumer set Name = %s , Email = %s ,Phone_number = %s ,Address = %s where consumer_id = %s"
        c.execute(query , [name , email , phone_number , address , id])
        conn.commit()
    except Exception as e:
        conn.rollback()

    return redirect(url_for('dashboard'))





if __name__ == '__main__':
    app.run(debug=True)

