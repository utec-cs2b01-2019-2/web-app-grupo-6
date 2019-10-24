from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import datetime
import json
import time

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)

@app.route("/login", methods = ["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.username == username
    ).filter(
        entities.User.password == password
    ).first()

    if user != None:
        return render_template('index.html')
    else:
        return "Sorry " +username+ " you are not a valid user"

def LstUsuarios():
    session = db.getSession(engine)

@app.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    return render_template('login.html')

@app.route('/users', methods = ['POST'])
def create_user():
   username = request.form['username']
   name = request.form['name']
   fullname = request.form['fullname']
   password = request.form['password']
   user = entities.User(
        username=username,
        name=name,
        fullname=fullname,
        password=password,
    )
   session = db.getSession(engine)
   session.add(user)
   session.commit()
   return 'Created User'

@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')

@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = dbResponse[:]
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c = json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'

@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    user = session.query(entities.User).filter(entities.User.id == id).one()
    session.delete(user)
    session.commit()
    return "Deleted User"

@app.route("/usuarios", methods = ["GET"])
def todos_los_usuarios():
    db_session=db.getSession(engine)
    users= db_session.query(entities.User);
    response = "";
    for user in users:
        response+= user.username+"-"+user.password+";"
    return response;

@app.route('/current', methods = ['GET'])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(entities.User.id == session['logged_user']).first()
    return Response(json.dumps(user,cls=connector.AlchemyEncoder),mimetype='application/json')


if __name__ == '__main__':
    app.secret_key = ".."
    app.run(debug=True,port=8000, threaded=True, host=('127.0.0.1'))
