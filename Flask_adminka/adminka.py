from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
import os, sys
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, make_response, render_template
import threading
import multiprocessing, time, signal
import psutil
from subprocess import check_output
app = Flask(__name__)
# from to_base import TestClass
from queue import Queue


app.config['SECRET_KEY'] = 'f9bf78b9a18ce6d46a0cd2b0b86df9da'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(290), nullable=False)
    commands = db.Column(db.String(290), nullable=False)
    status = db.Column(db.Boolean)
    pid = db.Column(db.Integer, nullable=True)


class BotsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    commands = TextAreaField('Commands', validators=[DataRequired()])
    submit = SubmitField('Save')


class ClockThread(threading.Thread):
    def __init__(self, queue):
        """Инициализация потока"""
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True

    def run(self):
        """Запуск потока"""
        # TestClass().start_1()
            # Получаем url из очереди
        bot_id = self.queue.get()
            # processs
        self.send_to_os(bot_id)

            # Отправляем сигнал о том, что задача завершена
        self.queue.task_done()


    def send_to_os(self, bot_id):
        bot1 = Bot.query.filter_by(id=bot_id).first()
        our_command = str(bot1.commands)
        os.system(f'python3 {our_command}')
        bot1.status = False
        db.session.commit()

# t = ClockThread(15)
# t.start()


@app.route("/")
@app.route("/index")
def home():
    bots = Bot.query.filter_by().all()
    return render_template('index.html', bots=bots)


@app.route("/")
@app.route("/index/<int:bot_id>/start")
def start_bot1(bot_id):
    bots = Bot.query.filter_by().all()
    bot = Bot.query.filter_by(id=bot_id).first()
    bot.status = True
    t = threading.Thread(target=send_to_os, args=(bot_id,))
    t.daemon = True
    t.start()
    db.session.commit()
    return render_template('index.html', bots=bots, bot_id=bot.id)


@app.route("/bot/new", methods=['GET', 'POST'])
def new_bot():
    form = BotsForm()
    if form.validate_on_submit():
        bot = Bot(name=form.name.data, commands=form.commands.data, pid=0)
        db.session.add(bot)
        db.session.commit()
        flash('Your bot has been created!', 'success')
        return redirect(url_for('.home'))
    return render_template('create_bot.html', title='New Bot', form=form, legend='New Bot')


@app.route("/bot/<int:bot_id>", methods=['GET', 'POST'])
def bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    return render_template('bot.html', title=bot.name, bot=bot)


@app.route("/bot/<int:bot_id>/start", methods=['GET', 'POST'])
def start_bot(bot_id):
    queue = Queue()
    bot = Bot.query.filter_by(id=bot_id).first()
    # if str(bot.status) == str('True'):
    #     flash('Your bot has been runed!', 'danger')
    #     return redirect(url_for('.bot', bot_id=bot.id))
    bot.status = True
    db.session.commit()
    global p, t
    queue.put(bot_id)
    t = ClockThread(queue)
    t.start()
    # p = multiprocessing.Process(target=TestClass().start_1(), args=(bot_id,))
    # pol = TestClass()
    # t = threading.Thread(target=TestClass().start_1(), args=(bot_id,))
    # t.daemon = True
    # t.start()
    # p.daemon = True
    # p.start()
    return render_template('bot.html', title=bot.name, bot=bot)


@app.route("/bot/<int:bot_id>/stop", methods=['GET', 'POST'])
def stop_bot(bot_id):
    bot2 = Bot.query.filter_by(id=bot_id).first()
    pid1 = str(bot2.pid)
    print(pid1)
    os.system(f"kill {pid1}")
    bot2.status = False
    db.session.commit()
    return render_template('bot.html', title=bot2.name, bot=bot2)



@app.route("/post/<int:bot_id>/update", methods=['GET', 'POST'])
def update_bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    form = BotsForm()
    if form.validate_on_submit():
        bot.name = form.name.data
        bot.commands = form.commands.data
        db.session.commit()
        flash('Your bot has been updated!', 'success')
        return redirect(url_for('.bot', bot_id=bot.id))
    elif request.method == 'GET':

        form.name.data = bot.name
        form.commands.data = bot.commands
    return render_template('create_bot.html', name='Update bot', form=form, legend='Update bot')


@app.route("/bot/<int:bot_id>/delete", methods=['POST'])
def delete_bot(bot_id):
    bot = Bot.query.get_or_404(bot_id)
    db.session.delete(bot)
    db.session.commit()
    flash('Your bot has been deleted!', 'success')
    return redirect(url_for('.home'))


def send_to_os(bot_id):
        bot1 = Bot.query.filter_by(id=bot_id).first()
        our_command = str(bot1.commands)
        os.system(f'python3 {our_command}')
        bot1.status = False
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)