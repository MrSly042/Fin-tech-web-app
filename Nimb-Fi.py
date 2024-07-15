from os import getenv as getvar
from flask import Flask, render_template, redirect, request
from flask import url_for, session, flash, jsonify
from datetime import timedelta, datetime as dt
import pytz
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import requests

load_dotenv('conf.env')

#environment variables for API connection
sql_url: str = getvar('url')
passphrase: str = getvar("pass")
secretkey: str = getvar("secret_key")

#SQL COMMAND BLOCK
get_email_db = "SELECT pass_w, first_name FROM school_proj where email = %s"
get_db = "SELECT * FROM school_proj"
add_db = " Insert into school_proj values (default, %s, %s, %s, %s, default, default, default) "
check_exist_db = " SELECT email FROM school_proj "
deposit_db = "Update school_proj set balance = %s where email = %s"
check_balance = "Select balance from school_proj where email = %s"
add_more_regadless = "UPDATE school_proj set balance = balance + %s where email = %s"

#Aliases of the SQL command variables to avoid mixups
payload = {
            "get_email": get_email_db,
            'return_all': get_db,
            'add_row': add_db,
            'get_exist': check_exist_db,

            'insert_args': "",
            "action": "",
            "passphrase": passphrase,

            "edit_db_bal": deposit_db,
            "edit_db_bal_2": add_more_regadless,
            "check_funds": check_balance,

          }

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = secretkey
app.permanent_session_lifetime = timedelta(minutes=45)

#This block handles session data and events ###
def is_session_expired():
    expiration_time = session.get('expiration_time')
    if expiration_time is None:
        return False
    return dt.now() > expiration_time

@app.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True
    session['expiration_time'] = dt.now() + app.permanent_session_lifetime

@app.before_request
def check_session_expiration():
    if 'user' in session and is_session_expired():
        session.clear()  # Clear session if expired
        return redirect(url_for('session_expired'))

@app.route('/session_expired')
def session_expired():
    flash('Your session has expired. Please log in again.')
    return redirect(url_for('login'))

#get time greeting
def get_part_of_day():
    current_hour = dt.now(pytz.timezone('America/Toronto')).hour
    if 5 <= current_hour < 12:
        return "Good Morning"
    elif 12 <= current_hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

#This is the main implementation for the banking stuff

def change_bal(user_amt, check):#acct_where): #see try_send_mon

    acct_where = session['email']
    val = (user_amt, acct_where)
    payload['insert_args'] = val

    if check == True:
        payload['action'] = 'edit_db_bal'

    else:
        payload['action'] = "edit_db_bal_2"

    requests.post(sql_url, json = payload)
    #reload page

def transfer():
    pass

def acct_state():
    arg_email = (session['email'], )
    payload['action'] = "check_funds"
    payload['insert_args'] = arg_email

    response = requests.post(sql_url, json = payload)
    data = response.json()

    return data['result'][0][0]

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/dashboard', methods=['POST', 'GET'])
def dash():
    if request.method == "POST" and "user" in session.keys():
        person = (session['user']).title()
        
        return render_template("dashboard.html", time_day = get_part_of_day(), user_get = person, acct_balance = acct_state())
    
    else:
        return redirect(url_for("login"))
    
#implementation for sending money
    
@app.route('/try_send_mon', methods=['POST', 'GET'])
def try_send_mon():
    if request.method == "POST":
        input_email = request.form.get('input_email')
        input_amt = int(request.form.get('input_amt'))

        if input_amt < 10:
            flash("error_Minimum Amount is $10!!")
            return jsonify({'status': 'success'})

        get_det_send_mon(input_email, input_amt)
        return jsonify({'status': 'success'})

    else:
        flash("error_Illegal redirection!!!")
        return jsonify({'status': 'success'})

def get_det_send_mon(input_email, input_amt):
    current = acct_state()
    if input_amt > current:
        print("Amount exceeds your current balance!")
        flash("error_Amount exceeds your current balance!")
        
    else: 
        new_amt = current - input_amt
        change_bal(new_amt, True)#input_email) # this logic should be implemented when the user sends
        #money to a created acct. Should check if recipients exists
        #Then add money to recipient, wont do that for now
        flash("success_Money has been sent successfully!")

################
#Implementation for funding account
@app.route('/try-fund_acc', methods=["POST", "GET"])
def try_fund_acc():
    if request.method == "POST":
        input_amt = int(request.form.get("input_amt"))

        if input_amt < 10:
            # flash("error_Invalid Amount!!")
            flash("error_Minimum Amount is $10!!")
            return jsonify({'status': 'success'})

        change_bal(input_amt, False)
        flash("success_Money has been deposited")
        return jsonify({'status': 'success'})

    else:
        flash("error_Illegal redirection!!!")
        return jsonify({'status': 'success'})

##############

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session.permanent = True
        user_email = request.form['email_txt']
        pass_word = request.form['pass_txt']

        val = (user_email, )

        payload['action'] = "get_email"
        payload["insert_args"] = val

        response = requests.post(sql_url, json = payload)
        data = response.json()

        exist = data["result"]

        if not exist:
            flash("error_Username does not exist!")
            return redirect(url_for('login'))
        
        if bcrypt.check_password_hash(exist[0][0], pass_word):

            flash(f"success_Welcome {exist[0][1]}")
            session['user'] = exist[0][1]
            session['email'] = user_email

            flash("success_Logged In")
            #display acct details
            return render_template("intermediate.html")
        
        else:
            flash("error_Unrecognized login!\nTry again")
            return redirect(url_for('login'))
                    
    else:
        if "user" in session:
            print(session)
            flash("info_Already logged in!")
            return render_template("intermediate.html")
        
        # return render_template('login.html')
        return render_template('log_temp.html')
    
    
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        pass_word = request.form['reg_pass_txt']
        conf_pass = request.form['reg_conf_txt']

        if pass_word == conf_pass:
                    
            first_name = request.form['reg_first_txt']
            last_name = request.form['reg_last_txt']
            user_email = request.form['reg_email_txt']

            payload['action'] = "get_exist"
            payload['insert_args'] = ''
            
            response = requests.post(sql_url, json = payload)

            data = response.json()
            fetch = [var for tup in data["result"] for var in tup]

            if user_email in fetch:
                flash("error_This email has been used already!")
                return redirect(url_for("login"))

            else:
                hash_pass = bcrypt.generate_password_hash(pass_word).decode("utf-8")

                val = (first_name, last_name, hash_pass, user_email)
                payload['action'] = "add_row"
                payload['insert_args'] = val

                requests.post(sql_url, json = payload)
                session['user'] = first_name
                session['email'] = user_email

                message_flash = f"success_You have registered successfully!\nWelcome {first_name}" #flash rejected f-strings
                flash(message_flash)

                return render_template("intermediate.html")
        
        else:
            flash("error_Passwords do not match!!")
            return redirect(url_for('signup'))
    
    else:
        # return render_template('login.html', passed = True)
        return render_template('log_temp.html', passed = True)

@app.route("/logout")
def logout():
    if "user" in session:
        session.pop('user', None)
        session.pop('email', None)
        flash("success_You have been logged out!")
        
        return redirect(url_for("login"))
    
    else:
        flash("error_You have not logged in!")
        return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)