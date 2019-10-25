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

@app.route('/create_test_users', methods = ['GET'])
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(name="David", fullname="Lazo", password="1234", username="qwerty")
    db_session.add(user)
    db_session.commit()
    return "Test user created!"

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

@app.route('/current', methods = ['GET'])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(entities.User.id == session['logged_user']).first()
    return Response(json.dumps(user,cls=connector.AlchemyEncoder),mimetype='application/json')

@app.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    return render_template('login.html')

#API de GRUPOS
#1. CREATE
@app.route('/groups', methods = ['POST'])
def create_group():
    c = json.loads(request.data)
    group = entities.Group(name=c['name'])
    session_db = db.getSession(engine)
    session_db.add(group)
    session_db.commit()
    return 'Created Group'

#2. READ
@app.route('/groups/<id>', methods = ['GET'])
def read_group(id):
    session_db = db.getSession(engine)
    group = session_db.query(entities.Group).filter(
        entities.Group.id == id).first()
    data = json.dumps(group, cls=connector.AlchemyEncoder)
    return  Response(data, status=200, mimetype='application/json')

@app.route('/groups', methods = ['GET'])
def get_all_groups():
    session_db = db.getSession(engine)
    dbResponse = session_db.query(entities.Group)
    data = dbResponse[:]
    return Response(json.dumps(data,
        cls=connector.AlchemyEncoder), mimetype='application/json')

# UPDATE
@app.route('/groups/<id>', methods = ['PUT'])
def update_group(id):
    session_db = db.getSession(engine)
    group = session_db.query(entities.Group).filter(entities.Group.id == id).first()
    c = json.loads(request.data)

    for key in c.keys():
        setattr(group, key, c[key])
    session.add(group)
    session.commit()
    return 'Updated GROUP'

# DELETE
@app.route('/groups/<id>', methods = ['DELETE'])
def delete_group(id):
    session_db = db.getSession(engine)
    user = session_db.query(entities.Group).filter(entities.Group.id == id).one()
    session_db.delete(user)
    session_db.commit()
    return "Deleted User"
#_____________________________________________________________________________________
@app.route('/perfil', methods=['GET'])
def get_perfil():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Perfil)
    data = []
    for perfil in dbResponse:
        data.append(perfil)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/perfil', methods = ['DELETE'])
def delete_perfil():
    id = request.form['key']
    session = db.getSession(engine)
    perfiles = session.query(entities.Perfil).filter(entities.Perfil.id == id)
    for perfil in perfiles:
        session.delete(perfil)
    session.commit()
    return "Deleted Perfil"

@app.route('/perfil', methods = ['POST'])
def create_perfil():
    message = json.loads(request.data)
    perfil_name = message['perfil_name']
    # 2. look in database
    db_session = db.getSession(engine)

    perfil= db_session.query(entities.Perfil
        ).filter(entities.Perfil.perfil_name == perfil_name
        ).first()

    if perfil != None:
        return 'NOT'

    else:
        c = json.loads(request.data)
        perfil = entities.Perfil(
            perfil_name=c['perfil_name'],
            perfil_email=c['perfil_email'],
            perfil_number=c['perfil_number'],
            perfil_description=c['perfil_description']
        )
        session = db.getSession(engine)
        session.add(perfil)
        session.commit()
        return 'OK'

@app.route('/perfil', methods = ['PUT'])
def update_perfil():
    session = db.getSession(engine)
    id = request.form['key']
    perfil = session.query(entities.Perfil).filter(entities.Perfil.id == id).first()
    c =json.loads(request.form['values'])
    for key in c.keys():
        setattr(perfil, key, c[key])
    session.add(perfil)
    session.commit()
    return 'Updated Perfil'
#_______________________________________________________________________________

if __name__ == '__main__':
    app.secret_key = ".."
    app.run(debug=True,port=8000, threaded=True, host=('127.0.0.1'))
