import sqlalchemy as sa
from .temp_db import SqlAlchemyBase
import sqlalchemy.orm as orm


class Books_tracker(SqlAlchemyBase):
    __tablename__ = 'books_tracker'
    id_books_tracker = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    author = sa.Column(sa.String, nullable=True)
    name = sa.Column(sa.String, nullable=True)
    start_date = sa.Column(sa.Date, nullable=True)
    end_date = sa.Column(sa.Date, nullable=True)
    short_description = sa.Column(sa.String, nullable=True)
    evaluation = sa.Column(sa.Integer, nullable=True)
    id_user = sa.Column(sa.Integer, sa.ForeignKey("user.id_user"))
    user = orm.relation('User')