from flask_sqlalchemy import SQLAlchemy
from googletrans import Translator
from flask import Flask, request, jsonify, make_response, render_template
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime
from functools import wraps


app = Flask(__name__)


app.config['SECRET_KEY'] = 'f9bf78b9a18ce6d46a0cd2b0b86df9da'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(290), nullable=False)
    title = db.Column(db.String(290), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(90))


dictionary = db.Table('dictionary',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('word_id', db.Integer, db.ForeignKey('word.id'), primary_key=True))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(60))
    admin = db.Column(db.Boolean)
    image_user = db.Column(db.String(20), nullable=False, default='default.jpg')


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100))
    translate = db.Column(db.String(100))
    user_id = db.Column(db.Integer)
    image_word = db.Column(db.String(90))
    user_dictionary = db.relationship('User', secondary=dictionary,
                                      backref=db.backref('dictionary', lazy='dynamic'))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

"""For users and users"""

@app.route("/")
@app.route("/index")
def home():
    return render_template('index.html')


@app.route('/user', methods=['GET'])
@token_required
def get_all_user(current_user):

    if not current_user. admin:
        return jsonify({'message': 'Cannot perform that function'})
    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users': output})


@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'Not user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['username'] = user.username
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'user': user_data})


@app.route('/user', methods=['POST'])
# @token_required
def create_user():
    # if not current_user.admin:
    #     return jsonify({'message': 'Cannot perform that function!'})
    data = request.get_json()

    hashed_pass = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_pass, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "New user was been created"})


@app.route('/api/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'Not user found!'})

    user.admin = True
    db.session.commit()
    return jsonify({'message': 'User has been promote'})


@app.route('/api/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'Not user found!'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'user has been deleted'})


@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html', title = 'Login')


@app.route('/api/login')
def api_login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW-Authenticate': 'Basic realm=Login required'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('could not verify', 401, {'WWW-Authenticate': 'Basic realm=Login required'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('utf-8')})

    return make_response('could not verify', 401, {'WWW-Authenticate': 'Basic realm=Login required'})



"""Posts"""

@app.route('/api/posts', methods=['GET'])
def get_all_posts():

    posts = Post.query.all()

    output = []

    for post in posts:
        post_data = {}
        post_data['id'] = post.id
        post_data['title'] = post.title
        post_data['content'] = post.content
        post_data['image'] = post.image_file
        post_data['date_posted'] = post.date_posted
        output.append(post_data)

    return jsonify({'posts': output})


@app.route('/api/post/<post_id>', methods=['GET'])
def api_get_one_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({'message': 'No post found!'})

    post_data = {}
    post_data['id'] = post.id
    post_data['title'] = post.title
    post_data['content'] = post.content
    post_data['image'] = post.image_file
    post_data['date-posted'] = post.date_posted

    return jsonify({'post': post_data})

@app.route('/post/<post_id>', methods=['GET'])
def get_one_post(post_id):
    return render_template('post.html', post_id=post_id)

"""Dictionary translate and words"""

@app.route('/api/translate', methods=['POST'])
def make_translate():
    data = request.get_json()
    word = data['translate']

    translator = Translator()
    language = 'ru'
    translate_word = (translator.translate(word, dest=language)).text
    return jsonify({'translate:': translate_word})


@app.route('/api/dictionary', methods=['GET'])
@token_required
def get_all_words(current_user):
    lop = [p for p in current_user.dictionary]
    if len(lop) is 0:
        return jsonify({'message': 'No words in dictionary!'})

    output = []
    for text in current_user.dictionary:
        user_dictionary = {}
        user_dictionary[text.word] = text.translate
        output.append(user_dictionary)

    return jsonify({'dictionary:': output})


@app.route('/api/dictionary', methods=['POST'])
@token_required
def add_word(current_user):
    data = request.get_json()
    word = data['translate']

    if word in Word.query.all():
        word1 = Word.query.filter_by(word=word).first()
        current_user.dictionary.append(word1)
        db.session.commit()
        return jsonify({'dictionary:': 'Added in dictionary!'})

    translator = Translator()
    language = 'ru'
    translate_word = (translator.translate(word, dest=language)).text

    new_word = Word(word=data['translate'], translate=translate_word)
    db.session.add(new_word)
    current_user.dictionary.append(new_word)
    db.session.commit()

    return jsonify({'translate:': 'Added in dictionary!'})


if __name__ == '__main__':
    app.run(debug=True)