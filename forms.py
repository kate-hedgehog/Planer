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
    description = StringField("Краткое описание")
    data =  DateField("Дата", validators=[DataRequired()], format='%d-%m-%Y' , default=datetime.today)
    start_time = TimeField("Время начала", validators=[DataRequired()], format='%H:%M' )
    end_time = TimeField("Время окончания", validators=[DataRequired()], format='%H:%M')
    important = IntegerField("Важность", validators=[DataRequired()])
    submit = SubmitField('Применить')


class AllTasksForm(FlaskForm):
    data_day =  DateField("Дата", validators=[DataRequired()], format='%Y-%m-%d' , default=datetime.today)
    data_week = DateField("Неделя с", validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today)
    data_month = DateField("Месяц с", validators=[DataRequired()], format='%Y-%m-%d', default=datetime.today)
    submit = SubmitField('Показать')


