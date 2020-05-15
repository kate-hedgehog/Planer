import sqlalchemy as sa
from .temp_db import SqlAlchemyBase
import sqlalchemy.orm as orm


class Water_tracker(SqlAlchemyBase):
    __tablename__ = 'water_tracker'
    id_water_tracker = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    number_drunk_glasses = sa.Column(sa.Integer)
    data = sa.Column(sa.Date, nullable=True)
    id_user = sa.Column(sa.Integer, sa.ForeignKey('user.id_user'))
    user = orm.relation('User')