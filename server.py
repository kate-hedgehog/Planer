import datetime

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from forms import LoginForm, RegistrationForm, TasksForm
from data.db_session import __all_models as models


now = datetime.datetime.now()


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'
db_session.global_init("db/plan.sqlite")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(models.user.User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    session = db_session.create_session()
    form = session.query(models.tasks.Tasks)#.filter(models.tasks.Tasks.data == now.strftime("%d-%m-%Y"))
    return render_template('index.html', title='Planer', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(models.user.User).filter(models.user.User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Вход', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация', form=form, message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(models.user.User).filter(models.user.User.login == form.login.data).first():
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = models.user.User(name=form.name.data, surname=form.surname.data, login=form.login.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/tasks',  methods=['GET','POST'])
@login_required
def add_tasks():
    form =TasksForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = models.tasks.Tasks()
        tasks.text_task = form.text_task.data
        tasks.description = form.description.data
        tasks.data = form.data.data
        tasks.start_time = form.start_time.data
        tasks.end_time = form.end_time.data
        tasks.id_important = form.important.data
        tasks.user = current_user
        session.merge(tasks)
        session.commit()
        return redirect('/')
    return render_template('tasks.html', title='Добавление Задачи', form=form)


@app.route('/alltasks',  methods=['GET','POST'])
def all_tasks():
    session = db_session.create_session()
    form = session.query(models.tasks.Tasks)  # .filter(models.tasks.Tasks.data == now.strftime("%d-%m-%Y"))
    return render_template('alltasks.html', title='Planer', form=form)


@app.route('/trackers',  methods=['GET','POST'])
def all_trackers():
    session = db_session.create_session()
    return render_template('trackers.html', title='Planer')


@app.route('/alltasks_week',  methods=['GET','POST'])
def all_tasks_week():
    session = db_session.create_session()
    return render_template('alltasks_week.html', title='Planer')


@app.route('/alltasks_month',  methods=['GET','POST'])
def all_tasks_month():
    session = db_session.create_session()
    return render_template('alltasks_month.html', title='Planer')

def main():
    app.run()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=8080, host='127.0.0.1')
