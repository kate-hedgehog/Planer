from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, TimeField, IntegerField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class TasksForm(FlaskForm):
    text_task = StringField('Задача', validators=[DataRequired()])
    data =  DateField('Дата', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today)
    start_time = TimeField('Время начала', validators=[DataRequired()], format='%H:%M')
    important = IntegerField('Приоритет', validators=[DataRequired()])
    submit = SubmitField('Применить')


class AllTasksForm(FlaskForm):
    data_day =  DateField('Дата', validators=[DataRequired()], format='%Y-%m-%d' , default=datetime.today)
    data_week = DateField('Неделя с', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today)
    submit = SubmitField('Показать')


class AddTrackBooks(FlaskForm):
    author = StringField('Автор', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    start_date = DateField('Дата начала чтения', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today)
    end_date = DateField('Дата окончания чтения', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today)
    short_description = StringField('Краткое описание')
    evalution = IntegerField('Оценка', validators=[DataRequired()])
    submit = SubmitField('Применить')


class AddTrackFilms(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    evalution = IntegerField('Оценка', validators=[DataRequired()])
    submit = SubmitField('Применить')





