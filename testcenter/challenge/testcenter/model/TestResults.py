import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from model import db, Serializer


class TestResult(db.Model, Serializer):
    __tablename__ = "testresults"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_type = db.Column(db.String)
    result = db.Column(db.String)
    test_date = db.Column(db.DateTime)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, test_type: str, result: str, test_date: datetime, user_id: str):
        self.test_type = test_type
        self.result = result
        self.test_date = test_date
        self.user = user_id

    def __repr__(self):
        return f"<TestResult {self.id}>"


