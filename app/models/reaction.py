from enum import Enum


class ReactionType(str, Enum):
    """Domain reaction for a post.

    Policy v1:
    - One user can have only one reaction per post.
    - Same reaction again means toggle off.
    - Different reaction replaces the previous one.
    - Post authors cannot react to their own posts.
    """

    # Useful review signal. Used for Confidence Score v1.
    # "This review was useful while deciding whether to buy."
    HELPFUL = "HELPFUL"

    # Same bad purchase experience signal. Used for Confidence Score v1.
    # "I bought this too, and the same thing happened to me."
    SAME_HERE = "SAME_HERE"

    # The review helped avoid buying the product. Used for Impact Score v1.
    # "This review helped me avoid buying this product."
    SAVED_MY_MONEY = "SAVED_MY_MONEY"
