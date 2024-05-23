from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Process(db.Model):
    __tablename__ = "process"
    __table_args__ = {'schema': 'public'}

    id = Column("id", String, primary_key=True, nullable=False)
    date_of_entry = Column("date_of_entry", String, nullable=False)
    process_number = Column("process_number", String,
                            nullable=False, unique=True)
    action_infraction = Column("action_infraction", String, nullable=False)
    details = relationship("Details", backref="process", lazy=True)


class Details(db.Model):
    __tablename__ = "details"
    __table_args__ = {'schema': 'public'}

    id = Column("id", Integer, primary_key=True,
                nullable=False, autoincrement=True)
    incident_number = Column("incident_number", String,
                             primary_key=False, nullable=False)
    date = Column("date", String, nullable=False)
    offended_actors = Column("offended_actors", String, nullable=False)
    defendants = Column("defendants", String, nullable=False)
    process_number = Column(
        "process_number",
        String,
        ForeignKey("public.process.process_number"), nullable=False)


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {'schema': 'public'}

    id = Column("id", Integer, primary_key=True,
                nullable=False, autoincrement=True)
    username = Column("username", String, nullable=False, unique=True)
    password = Column("password", String, nullable=False, unique=True)
    token = Column("token", String, nullable=True, unique=True)
