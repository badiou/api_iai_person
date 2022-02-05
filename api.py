import os
from flask_cors import CORS
# importer Flask
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy  # importer SQLAlchemy
#import urllib.parse
from urllib.parse import quote_plus
from dotenv import load_dotenv  # permet d'importer les variables d'environnement
load_dotenv()
#from flask_migrate import Migrate

app = Flask(__name__)  # Créer une instance de l'application
#pg_pswrd = os.environ.get('pgpswrd')

motdepasse = quote_plus(os.getenv('pswd_db'))

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:{}@localhost:5432/todog2".format(
    motdepasse)
# connexion à la base de données
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Créer une instance de BD

CORS(app)
#CORS(app, resources={r"/api/*": {"origins": "*"}})

# CORS Headers


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


class Person(db.Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }


db.create_all()


@app.route('/api')
def api():
    return jsonify({
        'name': 'OURO',
        'email': 'badiou'
    })

#################################################
#           Liste des personnes
####################################################


@app.route('/persons')
def get_all_persons():
    persons = Person.query.all()
    persons = [p.format() for p in persons]
    return jsonify(
        {
            'success': True,
            'persons': persons,
            'nombre': len(Person.query.all())}
    )


#################################################
#           selectioner une personne
####################################################
@app.route('/persons/<int:person_id>')
def one_person(person_id):
    try:
        person = Person.query.get(person_id)
        if person is None:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'id': person_id,
                'person': person.format()
            })
    except:
        abort(400)

#################################################
#           Ajouter une personne
####################################################


@app.route('/persons', methods=['POST'])
def add_person():
    body = request.get_json()
    new_name = body.get('name', None)
    new_email = body.get('email', None)
    person = Person(name=new_name, email=new_email)
    person.insert()
    persons = Person.query.all()
    persons_formatted = [p.format() for p in persons]
    return jsonify({
        'success': True,
        'created': person.id,
        'persons': persons_formatted,
        'total_persons': len(Person.query.all())
    })

#################################################
#           Modifier une personne
####################################################


@app.route('/persons/<int:person_id>', methods=['PATCH'])
def update_person(person_id):
    body = request.get_json()
    try:
        ma_person = Person.query.filter(Person.id == person_id).one_or_none()
        if ma_person is None:
            abort(404)
        if 'name' in body and 'email' in body:
            ma_person.name = body.get('name')
            ma_person.email = body.get('email')
        ma_person.update()
        return jsonify({
            'success': True,
            'id': ma_person.id,
            'personne_modifie': ma_person.format()
        })
    except:
        abort(400)


#################################################
#           Supprimer une personne
####################################################
@app.route('/persons/<int:person_id>', methods=['DELETE'])
def supprimer_personne(person_id):
    try:
        ma_person = Person.query.get(person_id)
        if ma_person is None:
            abort(404)
        else:
            ma_person.delete()
            return jsonify({
                "success": True,
                "deleted_id": person_id,
                "total_persons": len(Person.query.all())
            })
    except:
        abort(400)
    finally:
        db.session.close()
        

#ici on fait un get et la ressource 
#n'existe pas http://localhost:5000/persons/200
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not found"
        }), 404
    
@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal server error"
        }), 500
    
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400