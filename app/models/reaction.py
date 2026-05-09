from enum import Enum


# HELPFUL: The review was useful to the reader. Used for Confidence Score v1.
# SAME_HERE: The reader had the same or similar bad purchase experience. Used for Confidence Score v1.
# SAVED_MONEY: The review helped the reader avoid buying the product. Used for Impact Score v1.
class ReactionType(str, Enum):
    HELPFUL = "HELPFUL"
    SAME_HERE = "SAME_HERE"
    SAVED_MONEY = "SAVED_MONEY"
