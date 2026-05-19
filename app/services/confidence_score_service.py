from math import log1p

"""
confidence_score =
  min(log1p(same_here_count) / log1p(20) * 40, 40)
+ min(log1p(helpful_count) / log1p(30) * 30, 30)
+ min(log1p(comment_count) / log1p(20) * 20, 20)
+ min(image_count / 5 * 10, 10)

"""


def calculate_confidence_score(
    helpful_count: int,
    same_here_count: int,
    comment_count: int,
    image_count: int,
) -> float:
    helpful_score = min(log1p(helpful_count) / log1p(30) * 30, 30)
    same_here_score = min(log1p(same_here_count) / log1p(20) * 40, 40)
    comment_score = min(log1p(comment_count) / log1p(20) * 20, 20)
    image_score = min(image_count / 5 * 10, 10)

    return round(
        same_here_score + helpful_score + comment_score + image_score,
        1,
    )
