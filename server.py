from datetime import datetime, date, timedelta
import calendar
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from forms import LoginForm, RegistrationForm, TasksForm, AllTasksForm
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
    id = []
    session = db_session.create_session()
    data = date.today().strftime("%d-%m-%Y")
    form = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.data == data)
    return render_template('index.html', title='Planer', form=form, data=data)


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
def add_tasks(data, page):
    form = TasksForm()
    if request.method == "GET":
        data = datetime.strptime(data, '%d-%m-%Y').date()
        form.data.data = data
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = models.tasks.Tasks()
        tasks.text_task = form.text_task.data
        tasks.description = form.description.data
        tasks.data = form.data.data.strftime("%d-%m-%Y")
        tasks.start_time = form.start_time.data
        tasks.end_time = form.end_time.data
        tasks.id_important = form.important.data
        tasks.day = DAY_RU[form.data.data.strftime('%A')]
        tasks.user = current_user
        session.merge(tasks)
        session.commit()
        return redirect('/'+page)
    return render_template('tasks.html', title='Добавление Задачи', form=form)


@app.route('/change_tasks/<page>/<id_task>', methods=['GET', 'POST'])
@login_required
def change_tasks(id_task, page):
    form = TasksForm()
    if request.method == "GET":
        session = db_session.create_session()
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                         models.tasks.Tasks.user == current_user).first()
        if tasks:
            form.text_task.data = tasks.text_task
            form.description.data = tasks.description
            data = datetime.strptime(tasks.data, '%d-%m-%Y').date()
            form.data.data = data
            form.start_time.data = tasks.start_time
            form.end_time.data = tasks.end_time
            form.important.data = tasks.id_important
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.id_task == id_task,
                                                         models.tasks.Tasks.user == current_user).first()
        if tasks:
            tasks.text_task = form.text_task.data
            tasks.description = form.description.data
            tasks.data = form.data.data.strftime("%d-%m-%Y")
            tasks.start_time = form.start_time.data
            tasks.end_time = form.end_time.data
            tasks.id_important = form.important.data
            tasks.day = DAY_RU[form.data.data.strftime('%A')]
            session.commit()
            return redirect('/'+page)
        else:
            abort(404)
    return render_template('tasks.html', title='Добавление Задачи', form=form)


@app.route('/alltasks', methods=['GET', 'POST'])
def all_tasks():
    session = db_session.create_session()
    form = AllTasksForm()
    if form.validate_on_submit():
        data = form.data_day.data.strftime("%d-%m-%Y")
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.data == data)

        return render_template('alltasks.html', title='Planer', form=form, tasks=tasks, data=data)
    return render_template('alltasks.html', title='Planer', form=form)


@app.route('/trackers', methods=['GET', 'POST'])
def all_trackers():
    session = db_session.create_session()
    return render_template('trackers.html', title='Planer')


@app.route('/alltasks_week', methods=['GET', 'POST'])
def all_tasks_week():
    day_date = {}
    session = db_session.create_session()
    form = AllTasksForm()
    if form.validate_on_submit():
        tasks = session.query(models.tasks.Tasks).filter(models.tasks.Tasks.data >= form.data_week.data.strftime("%d-%m-%Y")) \
            .filter(models.tasks.Tasks.data <= (form.data_week.data + timedelta(weeks=1)).strftime("%d-%m-%Y"))
        for i in range(7):
            day_date[DAY_RU[(form.data_week.data + timedelta(days=i)).strftime('%A')]] = \
                (form.data_week.data + timedelta(days=i)).strftime("%d-%m-%Y")
        return render_template('alltasks_week.html', title='Planer', form=form, tasks=tasks, day_date=day_date)
    return render_template('alltasks_week.html', title='Planer', form=form, day_date=day_date)


@app.route('/alltasks_month', methods=['GET', 'POST'])
def all_tasks_month():
    NUMBER_OF_DAY = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6,
                     'Воскресенье': 7}
    first_week_for_out = {'Понедельник': '', 'Вторник': '', 'Среда': '', 'Четверг': '', 'Пятница': '', 'Суббота': '',
                          'Воскресенье': ''}
    first_week = []
    second_week = {}
    third_week = {}
    fourth_week = {}
    fifth_week = {}
    sixth_week = {}
    session = db_session.create_session()
    form = AllTasksForm()
    if form.validate_on_submit():
        if form.data_month.data.day == 1:
            count_days = int(calendar.monthrange(form.data_month.data.year, form.data_month.data.month)[1])
        else:
            count_days = 31
        tasks = session.query(models.tasks.Tasks)\
            .filter(models.tasks.Tasks.data >= form.data_month.data.strftime("%d-%m-%Y"))\
            .filter(models.tasks.Tasks.data <= (form.data_month.data + timedelta(days=25)).strftime("%d-%m-%Y"))
        tasks2 = session.query(models.tasks.Tasks)\
            .filter(models.tasks.Tasks.data >= (form.data_month.data + timedelta(days=26)).strftime("%d-%m-%Y")) \
            .filter(models.tasks.Tasks.data <= (form.data_month.data + timedelta(days=count_days)).strftime("%d-%m-%Y"))
        first = 8 - NUMBER_OF_DAY[DAY_RU[form.data_month.data.strftime('%A')]]
        for i in range(count_days):
            if i < first:
                first_week += [(DAY_RU[(form.data_month.data + timedelta(days=i)).strftime('%A')],
                                (form.data_month.data + timedelta(days=i)).strftime("%d-%m-%Y"))]
            elif first <= i < first+7:
                second_week[DAY_RU[(form.data_month.data + timedelta(days=i)).strftime('%A')]] = \
                    (form.data_month.data + timedelta(days=i)).strftime("%d-%m-%Y")
            elif first+7 <= i < first+14:
                third_week[DAY_RU[(form.data_month.data + timedelta(days=i)).strftime('%A')]] = \
                    (form.data_month.data + timedelta(days=i)).strftime("%d-%m-%Y")
            elif first+14 <= i < first+21:
                fourth_week[DAY_RU[(form.data_month.data + timedelta(days=i)).strftime('%A')]] = \
                    (form.data_month.data + timedelta(days=i)).strftime("%d-%m-%Y")
            elif first+21 <= i < first+28:
                fifth_week[DAY_RU[(form.data_month.data + timedelta(days=i)).strftime('%A')]] = \
                    (form.data_month.data + timedelta(days=i)).strftime("%d-%m-%Y")
            else:
                sixth_week[DAY_RU[(form.data_month.data + timedelta(days=i)).strftime('%A')]] = \
                    (form.data_month.data + timedelta(days=i)).strftime("%d-%m-%Y")
        first_week_for_out.update(first_week)
        for item in tasks:
            print(item.data)
        for item in tasks2:
            print(item.data)
        return render_template('alltasks_month.html', title='Planer', form=form, tasks=tasks,
                               first_week = first_week_for_out,second_week = second_week, third_week = third_week,
                               fourth_week = fourth_week, fifth_week = fifth_week, sixth_week = sixth_week)
    return render_template('alltasks_month.html', title='Planer', form=form)


def main():
    app.run()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=8080, host='127.0.0.1')
