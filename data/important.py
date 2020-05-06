import sqlalchemy as sa
import sqlalchemy.orm as orm
from .temp_db import SqlAlchemyBase

class Important(SqlAlchemyBase):
    __tablename__ = 'important'
    id_important = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    important = sa.Column(sa.String, nullable=True)
    tasks = orm.relation("Tasks", back_populates='important')