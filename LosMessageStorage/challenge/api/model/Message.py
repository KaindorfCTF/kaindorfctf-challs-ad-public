from model import db


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255))
    user = db.relationship('User', back_populates='messages')

    @classmethod
    def add_for_user(cls, user_id: int, message: str) -> bool:
        # if len(message) > 255:
        #     return False
        message_obj = cls(user_id=user_id, message=message)
        db.session.add(message_obj)
        db.session.commit()
        return True

    @classmethod
    def get_last_messages_from_user(cls, user_id: int, limit: int) -> list[str]:
        messages = cls.query.with_entities(cls.message).filter_by(user_id=user_id).order_by(cls.id.desc()).limit(
            limit).all()
        return [message[0] for message in messages]

    @classmethod
    def get_last_messages(cls, limit: int) -> list[tuple[int, str]]:
        messages = cls.query.with_entities(cls.message).order_by(cls.id.desc()).limit(limit).all()
        return [message[0] for message in messages]
