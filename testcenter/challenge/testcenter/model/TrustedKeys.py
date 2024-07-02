import uuid

from sqlalchemy import true
from sqlalchemy.dialects.postgresql import UUID

from model import db, Serializer


class TrustedKey(db.Model, Serializer):
    __tablename__ = "trustedkeys"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_key = db.Column(db.String)
    private_key = db.Column(db.String)
    is_signup_key = db.Column(db.Boolean)

    def __init__(self, public_key: str, private_key: str):
        self.public_key = public_key
        self.private_key = private_key

    def serialize(self):
        return Serializer.serialize(self)

    def __repr__(self):
        return f"<TrustedKey {self.id}>"

    @staticmethod
    def get_signup_key():
        return db.session.query(TrustedKey).filter(TrustedKey.is_signup_key == true()).first()

    @staticmethod
    def get_all() -> list:
        return db.session.query(TrustedKey).all()
