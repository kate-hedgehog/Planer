import sqlalchemy as sa
from .temp_db import SqlAlchemyBase
import sqlalchemy.orm as orm


class Execute(SqlAlchemyBase):
    __tablename__ = 'execute'
    id_execute = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    execute = sa.Column(sa.String, nullable=True)
    tasks = orm.relation("Tasks", back_populates='execute')