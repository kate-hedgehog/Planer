import sqlalchemy as sa
from .temp_db import SqlAlchemyBase
import sqlalchemy.orm as orm


class Films_tracker(SqlAlchemyBase):
    __tablename__ = 'films_tracker'
    id_films_tracker = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    evaluation = sa.Column(sa.Integer)
    id_user = sa.Column(sa.Integer, sa.ForeignKey('user.id_user'))
    user = orm.relation('User')