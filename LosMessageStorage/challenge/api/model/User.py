from __future__ import annotations

from model import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    messages = db.relationship('Message', back_populates='user')

    @classmethod
    def add(cls, username: str, password: str):
        if not cls.query.filter_by(username=username).first():
            user = cls(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return True
        return False

    @classmethod
    def does_exist(cls, username: str) -> bool:
        return db.session.query(cls.id).filter_by(username=username).first() is not None

    @classmethod
    def is_authenticated(cls, username: str, password: str) -> bool:
        return db.session.query(cls.id).filter_by(username=username, password=password).first() is not None

    @classmethod
    def get_id(cls, username: str) -> int | None:
        user = cls.query.filter_by(username=username).first()
        return user.id if user else None

    @classmethod
    def get_registered_users(cls, limit: int = 100) -> list[str]:
        return [user.username for user in cls.query.with_entities(cls.username).limit(limit).all()]
