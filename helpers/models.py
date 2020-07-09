from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import *
from mongoengine.queryset import CASCADE


class Member(Document):
    id = LongField(primary_key=True, required=True)
    muted = BooleanField(default=False)


class TempAction(Document):
    guild = LongField(required=True)
    member = ReferenceField(Member, reverse_delete_rule=CASCADE, required=True)
    action = StringField(choices=("mute", "ban"), required=True)
    expires = DateTimeField(required=True)


class RoleReact(Document):
    guild = LongField(required=True)
    channel = LongField(required=True)
    message = LongField(required=True, unique=True)
    name = StringField(required=True, unique=True)
    options = MapField(field=LongField())
