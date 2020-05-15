from datetime import datetime, date, timedelta
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_ngrok import run_with_ngrok
from data import db_session
from forms import LoginForm, RegistrationForm, TasksForm, AllTasksForm, AddTrackBooks, AddTrackFilms
from data.db_session import __all_models as models

app = Flask(__name__)
run_with_ngrok(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'
db_session.global_init('db/plan.sqlite')
NOW = date.today().strftime('%d-%m-%Y')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(models.user.User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        count_book, count_film = 0, 0
        session = db_session.create_session()
        date_task = NOW
        NAME_TRACK_BOOKS = ('Название', 'Автор', 'Краткое описание', 'Дата начала', 'Дата окончания', 'Оценка')
        NAME_TRACK_FILMS = ('Название', 'Оценка')
        tasks = session.query(models.tasks.Tasks) \
            .filter(models.tasks.Tasks.data == date_task, models.tasks.Tasks.user == current_user) \
            .order_by(models.tasks.Tasks.start_time)
        books = session.query(models.books_tracker.Books_tracker) \
            .filter(models.books_tracker.Books_tracker.user == current_user) \
            .order_by(models.books_tracker.Books_tracker.start_date)
        films = session.query(models.films_tracker.Films_tracker) \
            .filter(models.films_tracker.Films_tracker.user == current_user)
        for _ in books:
            count_book = 1
            break
        for _ in films:
            count_film = 1
            break
        return render_template('index.html', title='Planer', tasks=tasks, books=books, films=films,
                               name_track_books=NAME_TRACK_BOOKS, name_track_films=NAME_TRACK_FILMS,
                               data=date_task, count_book=count_book, count_film=count_film)
    return render_template('index.html', title='Planer')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(models.user.User).filter(models.user.User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Вход', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    param = {'title': 'Регистрация'}
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            param['message'] = 'Пароли не совпадают'
            return render_template('registration.html', form=form, **param)
        session = db_session.create_session()
        if session.query(models.user.User).filter(models.user.User.login == form.login.data).first():
            param['message'] = 'Такой пользователь уже есть'
            return render_template('registration.html', form=form, **param)
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
    return redirect('/')


@app.route('/tasks/<page>/<date_task>', methods=['GET', 'POST'])
@login_required
def add_tasks(page, date_task):
    form = TasksForm()
    if request.method == 'GET':
        form.data.data = datetime.strptime(date_task, '%d-%m-%Y').date()
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
        if page == 'index':
            return redirect('/' + page)
        else:
            return redirect('/' + page + '/' + date_task)
    return render_template('tasks.html', title='Добавление Задачи', form=form, data=date_task)


@app.route('/change_tasks/<page>/<select_date_task>/<id_task>', methods=['GET', 'POST'])
@login_required
def change_tasks(id_task, page, select_date_task):
    form = TasksForm()
    session = db_session.create_session()
    tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                     models.tasks.Tasks.user == current_user).first()
    if request.method == 'GET':
        if tasks:
            form.text_task.data = tasks.text_task
            date_task = datetime.strptime(tasks.data, '%d-%m-%Y').date()
            form.data.data = date_task
            form.start_time.data = tasks.start_time
            form.important.data = tasks.id_important
        else:
            abort(404)
    if form.validate_on_submit():
        if tasks:
            tasks.text_task = form.text_task.data
            tasks.data = form.data.data.strftime('%d-%m-%Y')
            tasks.start_time = form.start_time.data
            tasks.id_important = form.important.data
            session.commit()
            if page == 'index':
                return redirect('/' + page)
            else:
                return redirect('/' + page + '/' + select_date_task)
        else:
            abort(404)
    return render_template('tasks.html', title='Изменение Задачи', form=form)


@app.route('/delete_tasks/<page>/<date_task>/<id_task>', methods=['GET', 'POST'])
@login_required
def delete_tasks(id_task, page, date_task):
    session = db_session.create_session()
    tasks = session.query(models.tasks.Tasks) \
        .filter(models.tasks.Tasks.id_task == id_task, models.tasks.Tasks.user == current_user).first()
    if tasks:
        session.delete(tasks)
        session.commit()
    else:
        abort(404)
    if page == 'index':
        return redirect('/' + page)
    else:
        return redirect('/' + page + '/' + date_task)


@app.route('/alltasks/<date_tasks_day>', methods=['GET', 'POST'])
def all_tasks(date_tasks_day):
    session = db_session.create_session()
    form = AllTasksForm()
    if request.method == 'GET':
        form.data_day.data = datetime.strptime(date_tasks_day, '%d-%m-%Y').date()
        tasks = session.query(models.tasks.Tasks) \
            .filter(models.tasks.Tasks.data == date_tasks_day, models.tasks.Tasks.user == current_user) \
            .order_by(models.tasks.Tasks.start_time)
        return render_template('alltasks.html', title='Planer', form=form, tasks=tasks, data=date_tasks_day)
    if form.validate_on_submit():
        data_tasks_day = form.data_day.data.strftime('%d-%m-%Y')
        return redirect('/alltasks/' + data_tasks_day)
    return render_template('alltasks.html', title='Planer', form=form)


@app.route('/alltasks_week/<date_tasks_week>', methods=['GET', 'POST'])
def all_tasks_week(date_tasks_week):
    DAY_RU = {'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда', 'Thursday': 'Четверг',
              'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'}
    day_date = {}
    session = db_session.create_session()
    form = AllTasksForm()
    if request.method == 'GET':
        form.data_week.data = datetime.strptime(date_tasks_week, '%d-%m-%Y').date()
        tasks = session.query(models.tasks.Tasks) \
            .filter(models.tasks.Tasks.data >= date_tasks_week, models.tasks.Tasks.user == current_user) \
            .order_by(models.tasks.Tasks.start_time)
        for i in range(7):
            day_date[DAY_RU[(form.data_week.data + timedelta(days=i)).strftime('%A')]] = \
                (form.data_week.data + timedelta(days=i)).strftime('%d-%m-%Y')
        return render_template('alltasks_week.html', title='Planer', form=form, tasks=tasks, day_date=day_date,
                               data=date_tasks_week)
    if form.validate_on_submit():
        date_tasks_week = form.data_week.data.strftime('%d-%m-%Y')
        return redirect('/alltasks_week/' + date_tasks_week)
    return render_template('alltasks_week.html', title='Planer', form=form, day_date=day_date)


@app.route('/trackers', methods=['GET', 'POST'])
def all_trackers():
    date = NOW
    param = {'title': 'Planer', 'head': 'Трекеры'}
    TRACKERS = {'Трекер книг': 'book', 'Трекер фильмов': 'film'}
    return render_template('trackers.html', **param, trackers=TRACKERS, data=date)


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
    books = session.query(models.books_tracker.Books_tracker) \
        .filter(models.books_tracker.Books_tracker.id_books_tracker == id_book,
                models.books_tracker.Books_tracker.user == current_user).first()
    if books:
        session.delete(books)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/change_book_tracker/<id_book>', methods=['GET', 'POST'])
@login_required
def change_book_tracker(id_book):
    form = AddTrackBooks()
    session = db_session.create_session()
    books = session.query(models.books_tracker.Books_tracker). \
        filter(models.books_tracker.Books_tracker.id_books_tracker == id_book,
               models.books_tracker.Books_tracker.user == current_user).first()
    if request.method == 'GET':
        if books:
            form.author.data = books.author
            form.name.data = books.name
            form.start_date.data = datetime.strptime(books.start_date, '%d-%m-%Y').date()
            form.end_date.data = datetime.strptime(books.end_date, '%d-%m-%Y').date()
            form.short_description.data = books.short_description
            form.evalution.data = books.evaluation
        else:
            abort(404)
    if form.validate_on_submit():
        if books:
            books.author = form.author.data
            books.name = form.name.data
            books.start_date = form.start_date.data.strftime('%d-%m-%Y')
            books.end_date = form.end_date.data.strftime('%d-%m-%Y')
            books.short_description = form.short_description.data
            books.evaluation = form.evalution.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_track_books.html', title='Изменение Книги', form=form)


@app.route('/add_film_tracker', methods=['GET', 'POST'])
@login_required
def add_track_films():
    form = AddTrackFilms()
    if form.validate_on_submit():
        session = db_session.create_session()
        films_tracker = models.films_tracker.Films_tracker()
        films_tracker.name = form.name.data
        films_tracker.evaluation = form.evalution.data
        films_tracker.user = current_user
        session.merge(films_tracker)
        session.commit()
        return redirect('/')
    return render_template('add_track_films.html', title='Добавление фильма', form=form)


@app.route('/delete_film_tracker/<id_film>', methods=['GET', 'POST'])
@login_required
def delete_film_tracker(id_film):
    session = db_session.create_session()
    films = session.query(models.films_tracker.Films_tracker) \
        .filter(models.films_tracker.Films_tracker.id_films_tracker == id_film,
                models.films_tracker.Films_tracker.user == current_user).first()
    if films:
        session.delete(films)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/change_film_tracker/<id_film>', methods=['GET', 'POST'])
@login_required
def change_film_tracker(id_film):
    form = AddTrackFilms()
    session = db_session.create_session()
    films = session.query(models.films_tracker.Films_tracker) \
        .filter(models.films_tracker.Films_tracker.id_films_tracker == id_film,
                models.films_tracker.Films_tracker.user == current_user).first()
    if request.method == 'GET':
        if films:
            form.name.data = films.name
            form.evalution.data = films.evaluation
        else:
            abort(404)
    if form.validate_on_submit():
        if films:
            films.name = form.name.data
            films.evaluation = form.evalution.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_track_films.html', title='Изменение Фильма', form=form)


def main():
    app.run()


if __name__ == '__main__':
    app.run()
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)
    # app.run(debug=True, use_reloader=True, port=8080, host='127.0.0.1')
