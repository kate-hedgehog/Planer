import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .temp_db import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user'
    id_user = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    surname = sa.Column(sa.String, nullable=True)
    login = sa.Column(sa.String, index=True, unique=True, nullable=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    tasks = orm.relation('Tasks', back_populates='user')
    water_tracker = orm.relation('Water_tracker', back_populates='user')
    films_tracker = orm.relation('Films_tracker', back_populates='user')
    books_tracker = orm.relation('Books_tracker', back_populates='user')

    def set_password(self, password):  # устанавливает значение хеша пароля для переданной строки
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):  # проверяет, правильный ли пароль ввел пользователь
        return check_password_hash(self.hashed_password, password)

    def get_id(self):
        return self.id_user