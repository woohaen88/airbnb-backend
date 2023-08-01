from django.test import TestCase

from common.utils import DefaultObjectCreate
from direct_messages.models import ChattingRoom, Message


class DirectMessageModelTest(TestCase):
    def setUp(self) -> None:
        defaultObjectCreate = DefaultObjectCreate()
        self.user = defaultObjectCreate.create_user()

    def test_create_chatting_room(self):
        chatting_room = ChattingRoom.objects.create()
        chatting_room.users.add(self.user)

        for user in chatting_room.users.all():
            self.assertEqual(user.email, self.user.email)

        self.assertEqual("Chatting Room.", str(chatting_room))

    def test_create_message(self):
        text = "hahahoho"

        # chat_room
        chatting_room = ChattingRoom.objects.create()
        chatting_room.users.add(self.user)

        message = Message.objects.create(
            text=text,
            user=self.user,
            chatting_room=chatting_room,
        )

        results = map(lambda x: hasattr(message, x), ["text", "chatting_room", "user"])
        for result in results:
            self.assertTrue(result)

        self.assertEqual(
            f"{message.user} says: {message.text}",
            str(message),
        )
