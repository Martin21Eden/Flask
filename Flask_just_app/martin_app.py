from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import datetime
import os
from forms import RegisterForm, SongForm
from models import User, Song
from database import db_session, init_db
from passlib.hash import sha256_crypt
# from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/songs')
def songs():
    result = Song.query.all()
    if len(result) > 0:
        return render_template('songs.html', songs=result)
    else:
        flash('Songs have not found', 'danger')
        return render_template('songs.html')


@app.route('/song/<string:id>/')
def song(id):
    result = Song.query.filter_by(id=id).first()
    return render_template('song.html', song=result)


@app.route("/register", methods=('GET', 'POST'))
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # connection.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
        #             (name, email, username, password))
        signup = User(name=form.name.data, email=form.email.data, username = form.username.data, password=sha256_crypt.encrypt(str(form.password.data)))
        db_session.add(signup)
        db_session.commit()
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        result = User.query.filter_by(username=username).first()
        if result is not None:
            if sha256_crypt.verify(password_candidate, result.password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
        else:
            error = 'login unsuccessful. Check Username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#             return redirect(url_for('dashboard'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email = form.email.data).first()
#         if user and sha256_crypt.verify(user.password, form.password.data):
#             session['logged_in'] = True
#                 session['username'] = username
#                 flash('You are now logged in', 'success')
#                 return redirect(url_for('dashboard'))
#         else:
#             flash('login unsuccessful. Check email or password', 'danger')
#     return render_template('login.html', title = 'Login', form=form)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/dashboard')
@is_logged_in
def dashboard():
    result = Song.query.all()
    if len(result) > 0:
        return render_template('dashboard.html', songs=result)
    else:
        flash('Songs have not found', 'danger')
        return render_template('dashboard.html')


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/add_song', methods=['GET', 'POST'])
@is_logged_in
def add_song():
    form = SongForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        lyrics = form.lyrics.data
        song = Song(title=title, lyrics=lyrics, author=session['username'])
        db_session.add(song)
        db_session.commit()
        # cur.execute("INSERT INTO songs(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))
        flash('song Created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_song.html', form=form)


# Edit song
@app.route('/edit_song/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_song(id):
    result = Song.query.filter_by(id=id).first()
    form = SongForm()
    form.title.data = result.title
    form.lyrics.data = result.lyrics

    if request.method == 'POST' and form.validate():
        result.title = request.form['title']
        result.lyrics = request.form['lyrics']
        db_session.commit()
        flash('Your post has been updated!', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_song.html', form=form)
#
# Delete song
@app.route('/delete_song/<string:id>', methods=['POST'])
@is_logged_in
def delete_song(id):
    song = Song.query.filter_by(id=id).first()
    db_session.delete(song)
    db_session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
