from datetime import datetime, date, timedelta
import calendar
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from forms import LoginForm, RegistrationForm, TasksForm, AllTasksForm, AddTrackBooks
from data.db_session import __all_models as models

now = datetime.today().strftime("%Y-%d-%m")
DAY_RU = {'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда', 'Thursday': 'Четверг',
          'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'}

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
    count = 0
    session = db_session.create_session()
    data = date.today().strftime("%d-%m-%Y")
    NAME_TRACK_BOOKS = ('Название', 'Автор', 'Краткое описание', 'Дата начала', 'Дата окончания', 'Оценка')
    form = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.data == data,
                                                    models.tasks.Tasks.user == current_user).\
        order_by(models.tasks.Tasks.start_time)
    books = session.query(models.books_tracker.Books_tracker).\
        filter(models.books_tracker.Books_tracker.user == current_user).\
        order_by(models.books_tracker.Books_tracker.start_date)
    for item in books:
        count = 1
        break

    return render_template('index.html', title='Planer', form=form, books=books,name_track_books=NAME_TRACK_BOOKS,
                           data=data, count=count)

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


@app.route('/tasks/<page>/<data>', methods=['GET', 'POST'])
@login_required
def add_tasks(page, data):
    form = TasksForm()
    if request.method == "GET":
        form.data.data = datetime.strptime(data, '%d-%m-%Y').date()
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = models.tasks.Tasks()
        tasks.text_task = form.text_task.data
        tasks.data = form.data.data.strftime('%d-%m-%Y')
        tasks.start_time = form.start_time.data
        tasks.id_important = form.important.data
        tasks.user = current_user
        session.merge(tasks)
        session.commit()
        return redirect('/'+page)
    return render_template('tasks.html', title='Добавление Задачи', form=form, data=data)


@app.route('/change_tasks/<page>/<data>/<id_task>', methods=['GET', 'POST'])
@login_required
def change_tasks(id_task, page, data):
    form = TasksForm()
    if request.method == "GET":
        session = db_session.create_session()
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                         models.tasks.Tasks.user == current_user).first()
        if tasks:
            form.text_task.data = tasks.text_task
            data = datetime.strptime(tasks.data, '%d-%m-%Y').date()
            form.data.data = data
            form.start_time.data = tasks.start_time
            form.important.data = tasks.id_important
            print(form.important.data)
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                         models.tasks.Tasks.user == current_user).first()
        if tasks:
            tasks.text_task = form.text_task.data
            tasks.data = form.data.data.strftime("%d-%m-%Y")
            tasks.start_time = form.start_time.data
            tasks.id_important = form.important.data
            session.commit()
            return redirect('/'+page+'/'+data)
        else:
            abort(404)
    return render_template('tasks.html', title='Изменение Задачи', form=form)


@app.route('/delete_tasks/<page>/<data>/<id_task>', methods=['GET', 'POST'])
@login_required
def delete_tasks(id_task, page, data):
    session = db_session.create_session()
    tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                     models.tasks.Tasks.user == current_user).first()
    if tasks:
        session.delete(tasks)
        session.commit()
    else:
        abort(404)
    return redirect('/'+page+'/'+data)

@app.route('/alltasks/<data>', methods=['GET', 'POST'])
def all_tasks(data):
    session = db_session.create_session()
    form = AllTasksForm()
    if request.method == "GET":
        form.data_day.data = datetime.strptime(data, '%d-%m-%Y').date()
        data = form.data_day.data.strftime("%d-%m-%Y")
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.data == data,
                                                         models.tasks.Tasks.user == current_user). \
            order_by(models.tasks.Tasks.start_time)
        return render_template('alltasks.html', title='Planer', form=form, tasks=tasks, data=data)
    if form.validate_on_submit():
        data = form.data_day.data.strftime("%d-%m-%Y")
        return redirect('/alltasks/'+data)
    return render_template('alltasks.html', title='Planer', form=form)


@app.route('/alltasks_week/<data>', methods=['GET', 'POST'])
def all_tasks_week(data):
    day_date = {}
    session = db_session.create_session()
    form = AllTasksForm()
    if request.method == "GET":
        form.data_week.data = datetime.strptime(data, '%d-%m-%Y').date()
        data = form.data_week.data.strftime("%d-%m-%Y")
        tasks = session.query(models.tasks.Tasks).\
            filter(models.tasks.Tasks.data >= data,
                   models.tasks.Tasks.user == current_user).order_by(models.tasks.Tasks.start_time)
        for i in range(7):
            day_date[DAY_RU[(form.data_week.data + timedelta(days=i)).strftime('%A')]] = \
                    (form.data_week.data + timedelta(days=i)).strftime("%d-%m-%Y")
        return render_template('alltasks_week.html', title='Planer', form=form, tasks=tasks, day_date=day_date,
                               data=data)
    if form.validate_on_submit():
        data = form.data_week.data.strftime("%d-%m-%Y")
        tasks = session.query(models.tasks.Tasks).\
            filter(models.tasks.Tasks.data >= data,
                   models.tasks.Tasks.user == current_user).order_by(models.tasks.Tasks.start_time)
        for i in range(7):
            day_date[DAY_RU[(form.data_week.data + timedelta(days=i)).strftime('%A')]] = \
                (form.data_week.data + timedelta(days=i)).strftime("%d-%m-%Y")
        return render_template('alltasks_week.html', title='Planer', form=form, tasks=tasks, day_date=day_date, data=data)
    return render_template('alltasks_week.html', title='Planer', form=form, day_date=day_date)


@app.route('/trackers', methods=['GET', 'POST'])
def all_trackers():
    trackers = ('Трекер книг','Трекер фильмов', 'Трекер питья воды')
    return render_template('trackers.html', title='Planer', head = 'Трекеры', trackers=trackers)


@app.route('/add_book_tracker', methods=['GET', 'POST'])
@login_required
def add_track_books():
    form = AddTrackBooks()
    if form.validate_on_submit():
        session = db_session.create_session()
        books_tracker = models.books_tracker.Books_tracker()
        books_tracker.author = form.author.data
        books_tracker.name = form.name.data
        books_tracker.start_date = form.start_date.data.strftime('%d-%m-%Y')
        books_tracker.end_date = form.end_date.data.strftime('%d-%m-%Y')
        books_tracker.short_description = form.short_description.data
        books_tracker.evaluation = form.evalution.data
        books_tracker.user = current_user
        session.merge(books_tracker)
        session.commit()
        return redirect('/')
    return render_template('add_track_books.html', title='Добавление книги', form=form)


@app.route('/delete_book_tracker/<id_book>', methods=['GET', 'POST'])
@login_required
def delete_book_tracker(id_book):
    session = db_session.create_session()
    books = session.query(models.books_tracker.Books_tracker).\
        filter(models.books_tracker.Books_tracker.id_books_tracker == id_book,
                                                     models.tasks.Tasks.user == current_user).first()
    if books:
        session.delete(books)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/change_book_tracker/<id_book>', methods=['GET', 'POST'])
@login_required
def change_book_tracker(id_task, page, data):
    form = TasksForm()
    if request.method == "GET":
        session = db_session.create_session()
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                         models.tasks.Tasks.user == current_user).first()
        if tasks:
            form.text_task.data = tasks.text_task
            data = datetime.strptime(tasks.data, '%d-%m-%Y').date()
            form.data.data = data
            form.start_time.data = tasks.start_time
            form.important.data = tasks.id_important
            print(form.important.data)
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                         models.tasks.Tasks.user == current_user).first()
        if tasks:
            tasks.text_task = form.text_task.data
            tasks.data = form.data.data.strftime("%d-%m-%Y")
            tasks.start_time = form.start_time.data
            tasks.id_important = form.important.data
            session.commit()
            return redirect('/'+page+'/'+data)
        else:
            abort(404)
    return render_template('tasks.html', title='Изменение Задачи', form=form)


def main():
    app.run()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=8080, host='127.0.0.1')
