from decimal import Decimal

import anyio

from app.services.category_score_summary import get_category_score_summary


class FakeResult:
    def __init__(self, row):
        self.row = row

    def one(self):
        return self.row


class FakeDb:
    def __init__(self, row):
        self.row = row

    async def execute(self, query):
        return FakeResult(self.row)


def test_category_score_summary_returns_average_when_enough_posts():
    async def run_test():
        db = FakeDb((10, Decimal("75.00")))

        summary = await get_category_score_summary(
            db=db,
            category="electronics",
            current_score=Decimal("80.00"),
        )

        assert summary["has_enough_data"] is True
        assert summary["category_average_score"] == Decimal("75.00")
        assert summary["score_delta"] == Decimal("5.00")
        assert summary["category_post_count"] == 10

    anyio.run(run_test)


def test_category_score_summary_hides_average_when_not_enough_posts():
    async def run_test():
        db = FakeDb((3, Decimal("75.00")))

        summary = await get_category_score_summary(
            db=db,
            category="electronics",
            current_score=Decimal("80.00"),
        )

        assert summary["has_enough_data"] is False
        assert summary["category_average_score"] is None
        assert summary["score_delta"] is None
        assert summary["category_post_count"] == 3

    anyio.run(run_test)
