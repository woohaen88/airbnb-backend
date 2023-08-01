from django.test import TestCase

from common.utils import DefaultObjectCreate


class MediaModelTest(TestCase):
    def setUp(self) -> None:
        defaultObjectCreate = DefaultObjectCreate()
        self.user = defaultObjectCreate.create_user()
        self.room = defaultObjectCreate.create_room(owner=self.user)
        self.experience = defaultObjectCreate.create_experience(host=self.user)

    def test_photo_model(self):
        """
        photo 모델 생성
        """
        pass

    def test_file_model(self):
        """
        photo 모델 생성
        """
        pass
