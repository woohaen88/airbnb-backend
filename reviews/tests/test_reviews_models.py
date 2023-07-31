from django.test import TestCase
from common.utils import DefaultObjectCreate
from reviews.models import Review


class ReviewTest(TestCase):
    """
    Review Model Test

    TODO:
    Review object는 f"{self.user} / {self.rating}" 형태 [v]
    """

    def setUp(self) -> None:
        defaultObjectCreate = DefaultObjectCreate()
        self.user = defaultObjectCreate.create_user()
        self.room = defaultObjectCreate.create_room(owner=self.user)
        self.experience = defaultObjectCreate.create_experience(host=self.user)

    def create_reviews_model(self):
        review = Review.objects.create(
            user=self.user,
            room=self.room,
            experience=self.experience,
            payload="hahaha",
            rating=3,
        )

        self.assertEqual(f"{review.user} / {review.rating}", str(review))
