import psycopg2
import jwt
from flask import Flask, request, jsonify
from datetime import datetime, timedelta 
from functools import wraps  
from flask_bcrypt import Bcrypt
from flask_bcrypt import generate_password_hash
from flask_bcrypt import check_password_hash

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = "this is secret"

def db_conn():
    conn = psycopg2.connect(database="flask_jwt",host="localhost",user="postgres",password="1719",port="5432")
    return conn 

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 403
        try:
            # Extract the token from the "Bearer" string
            token = token.split(" ")[1]
            # Decode and verify the token
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Pass the decoded payload to the decorated function
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 403

    return decorated 
						
@app.route('/all_users',methods=['GET'])
@token_required 
def get_all_users():
    conn = db_conn()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM users''')
    data=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(data)
        
@app.route('/signup',methods=['POST'])
def signup():
    conn = db_conn()
    cur =conn.cursor()
    data=request.json
    id = data.get("id")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cur.execute('''INSERT INTO users(id,name,email,password) VALUES(%s,%s,%s,%s)''',(id,name, email, hashed_password))
    conn.commit()
    cur.close()
    conn.close()
    return "Registerd successfully"

@app.route('/login', methods=['POST'])
def login():
    conn = db_conn()
    cur = conn.cursor()
    data = request.json
    email = data.get("email")
    password = data.get("password")
    cur.execute('''SELECT password FROM users where email=%s''',(email,))
    user = cur.fetchone()
    if user:
        hashed_password = user[0]
        if check_password_hash(hashed_password,password):
            token = jwt.encode({
                'email': email,
                'exp' : datetime.utcnow() + timedelta(seconds = 900)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'token': token }), 201
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        return jsonify({'error': 'User not found'}), 404     
    
@app.route("/access",methods=['GET'])
@token_required
def access():
    return jsonify({'message': 'valid jwt token'})
    
if __name__ == '__main__':
    app.run(debug=True)
    
    