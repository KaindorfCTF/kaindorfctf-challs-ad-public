from datetime import datetime
from flask_login import UserMixin
from model import db, Serializer
from model.TestResults import TestResult


class User(UserMixin, db.Model, Serializer):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    cert = db.Column(db.String)
    is_admin = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime)
    test_results = db.relationship("TestResult")

    def __init__(self, username: str, password: str, cert: bytes, is_admin: bool, creation_date: datetime):
        self.username = username
        self.password = password
        self.cert = cert
        self.is_admin = is_admin
        self.creation_date = creation_date

    def __repr__(self):
        return f"<User {self.id}>"

    def serialize(self):
        user = Serializer.serialize(self)
        # del user['test_results']
        # del user['cert']
        # del user['password']
        # del user['password']
        # DEBUG ONLY
        test_results = [TestResult.serialize(test_result) for test_result in self.test_results]
        user['test_results'] = test_results
        return user

    @staticmethod
    def get_all() -> list:
        return db.session.query(User).all()

    @staticmethod
    def get_user_by_id(user_id: int):
        return db.session.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_latest_users() -> list:
        users = db.session.query(User).outerjoin(TestResult).group_by(User).having(
            db.func.count(TestResult.id) > 0).all()
        return users

    @staticmethod
    def add_test_result(user_id: int, test_result: TestResult):
        user = db.session.query(User).filter(User.id == user_id).first()
        test_results = user.test_results
        test_results.append(test_result)

        user.test_results = test_results
        db.session.commit()
