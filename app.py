from crypt import methods
from os import abort
from flask import Flask, jsonify, redirect, render_template,request, url_for #importer Flask
from flask_sqlalchemy import SQLAlchemy #importer SQLAlchemy
#import urllib.parse
from urllib.parse import quote_plus
from flask_migrate import Migrate

app = Flask(__name__) #Créer une instance de l'application
motdepasse=quote_plus("B@diou2015")

app.config['SQLALCHEMY_DATABASE_URI']="postgresql://postgres:{}@localhost:5432/todog2".format(motdepasse)
#connexion à la base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app) #Créer une instance de BD
#migrate = Migrate(app, db)

class Person(db.Model):
    __tablename__='persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email=db.Column(db.String(100),unique=True)
db.create_all()

@app.route('/api')
def api():
    return jsonify({
        'name':'OURO',
        'email':'badiou'
    })
@app.route('/',methods=['GET'])
def index():
    person=Person.query.first()
    return "je suis dans la joie "+person.name
#ici on va vers la route


@app.route('/persons',methods=['GET'])
def all_persons(): 
    #ici on va vers le controlleur
    personnes=Person.query.all()
    return render_template('index.html',data=personnes)


@app.route('/add',methods=['POST','GET'])
def add():
    try:
        if request.method=='GET':
            return render_template('create.html')
        elif request.method=='POST': 
            f_name=request.form.get('name')
            f_email=request.form.get('email')
            person=Person(name=f_name,email=f_email)
            db.session.add(person)
            db.session.commit()
            return redirect(url_for('all_persons'))
    except:
        db.session.rollback()
    finally:
        db.session.close()

    
    
    