import sqlalchemy as sa
from .temp_db import SqlAlchemyBase
import sqlalchemy.orm as orm


class Tasks(SqlAlchemyBase):
    __tablename__ = 'tasks'
    id_task = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text_task = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.String, nullable=True)
    data = sa.Column(sa.Date, nullable=True)
    start_time = sa.Column(sa.Time, nullable=True)
    end_time = sa.Column(sa.Time, nullable=True)
    day = sa.Column(sa.String, nullable=True)
    id_user = sa.Column(sa.Integer, sa.ForeignKey("user.id_user"))
    user = orm.relation('User')
    id_important = sa.Column(sa.Integer, sa.ForeignKey("important.id_important"))
    important = orm.relation('Important')
    id_execute = sa.Column(sa.Integer, sa.ForeignKey("execute.id_execute"))
    execute = orm.relation('Execute')