from django.test import TestCase
from common.utils import (
    create_user,
    create_room,
    create_experience,
)
from reviews.models import Review


class ReviewTest(TestCase):
    """
    Review Model Test

    TODO:
    Review object는 f"{self.user} / {self.rating}" 형태 [v]
    """

    def setUp(self) -> None:
        self.user = create_user()
        self.room = create_room(owner=self.user)
        self.experience = create_experience(host=self.user)

    def create_reviews_model(self):
        review = Review.objects.create(
            user=self.user,
            room=self.room,
            experience=self.experience,
            payload="hahaha",
            rating=3,
        )

        self.assertEqual(f"{review.user} / {review.rating}", str(review))
