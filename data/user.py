import sqlalchemy as sa
import sqlalchemy.orm as orm
from .temp_db import SqlAlchemyBase

class User(SqlAlchemyBase):
    __tablename__ = 'user'
    id_user = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=True)
    surname = sa.Column(sa.String, nullable=True)
    login = sa.Column(sa.String, index=True, unique=True, nullable=True)
    hashed_password = sa.Column(sa.String, nullable=True)
    tasks = orm.relation("Tasks", back_populates='user')
    water_tracker = orm.relation("Water_tracker", back_populates='user')
    films_tracker = orm.relation("Films_tracker", back_populates='user')
    books_tracker = orm.relation("Books_tracker", back_populates='user')



