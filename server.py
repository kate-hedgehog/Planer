from flask import Flask, url_for, request, render_template, redirect
from data import db_session
from forms import LoginForm, RegistrationForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
db_session.global_init("db/plan.sqlite")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Planer')


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Вход', form=form)


@app.route('/registration')
def registration():
    form = RegistrationForm()
    return render_template('registration.html', title='Регистрация', form=form)



def main():
    app.run()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=8080, host='127.0.0.1')
