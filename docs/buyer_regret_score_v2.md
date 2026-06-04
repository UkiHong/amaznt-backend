# Buyer Regret Score v2 Design

Status: Implemented through Week 8 Day 7

This document describes the Buyer Regret Score v2 design for Amazn't. The v2 calculation service is implemented in `app/services/buyer_regret_score_service.py`.

## Goal

Buyer Regret Score v1 is based only on the author's own regret inputs. That keeps the MVP simple, but it also means a post author can overstate the severity of a product failure.

Buyer Regret Score v2 keeps the author score as the base, then applies a capped community validation signal. The goal is to make the score more community-aware without letting a small number of users hijack the score.

## Design Principles

- Keep the author score as the primary source of product failure severity.
- Use community validation as a correction signal, not the whole score.
- Increase community influence only when there is enough validation data.
- Include signals that describe product failure severity.
- Exclude signals that describe post impact rather than product failure severity.
- Keep the formula explainable for portfolio review and interviews.

## Inputs

### Author Score

`author_score` is the existing Buyer Regret Score v1.

It is calculated from:

```text
value_regret_score
description_mismatch_score
quality_disappointment_score
funniness_score
anger_score
```

Current v1 formula:

```text
author_score =
  value_regret_score * 0.30
+ description_mismatch_score * 0.25
+ quality_disappointment_score * 0.20
+ funniness_score * 0.10
+ anger_score * 0.15
```

### Community Validation Signals

Buyer Regret Score v2 uses:

```text
SAME_HERE
AGREE
DISAGREE
```

Meaning:

```text
SAME_HERE = another user experienced the same product failure
AGREE = the user agrees this is a valid product failure case
DISAGREE = the user thinks the post is exaggerated or not clearly a product failure
```

## Excluded Signal

`SAVED_MY_MONEY` is excluded from Buyer Regret Score v2.

Reason:

```text
SAVED_MY_MONEY measures whether the post changed a user's buying decision.
That is post impact, not product failure severity.
```

`SAVED_MY_MONEY` remains dedicated to:

```text
estimated_money_saved = saved_my_money_count * price_paid
Wallet Saved ranking
```

## Community Verdict Policy

Implemented verdict types:

```text
AGREE
DISAGREE
```

Policy:

```text
One user can leave one verdict per post.
Tapping the same verdict again toggles it off.
Tapping a different verdict replaces the previous verdict.
Post authors cannot leave verdicts on their own posts.
Database constraint: UNIQUE(user_id, post_id).
```

Implemented endpoint:

```text
POST /posts/{post_id}/verdicts/{verdict_type}
```

Response shape:

```text
status: created | updated | deleted
post_id
verdict_type
```

Post detail also returns:

```text
verdict_summary
my_verdict
```

## Formula Direction

### Positive and Negative Validation Counts

```text
positive_validation_count =
  same_here_count + agree_count

negative_validation_count =
  disagree_count
```

### Community Validation Score

```text
community_validation_score =
  (positive_validation_count + 2)
  / (positive_validation_count + negative_validation_count + 4)
  * 100
```

The `+2` and `+4` values act as smoothing.

Without smoothing, one `AGREE` could push the community score too close to 100. With smoothing, early community signals move the score gradually instead of creating extreme values.

Examples:

```text
No validation:
(0 + 2) / (0 + 0 + 4) * 100 = 50

One positive validation:
(1 + 2) / (1 + 0 + 4) * 100 = 60

One negative validation:
(0 + 2) / (0 + 1 + 4) * 100 = 40
```

### Dynamic Community Weight

Community validation should not always receive the full 35% weight. It should grow as validation data grows.

```text
total_validation_count =
  same_here_count + agree_count + disagree_count
```

```text
community_weight =
  min(log1p(total_validation_count) / log1p(20) * 0.35, 0.35)
```

Meaning:

```text
When there is no community validation, community_weight is 0.
As validation grows, community_weight increases.
The maximum community weight is 0.35.
```

### Final v2 Score

```text
buyer_regret_score_v2 =
  author_score * (1 - community_weight)
+ community_validation_score * community_weight
```

At maximum community influence:

```text
author_score weight = 0.65
community validation weight = 0.35
```

## Why 65:35 At Maximum

Amazn't is a community-based product failure platform, so community validation should matter. However, the author score should still remain the primary source because the author provides the original structured failure report.

The 65:35 maximum split gives community signals meaningful influence while keeping the score anchored to the original report.

## Relationship to Other Metrics

### Confidence Score

Confidence Score answers:

```text
How trustworthy or well-supported is this post?
```

It uses signals such as:

```text
SAME_HERE
HELPFUL
comment_count
image_count
```

### Estimated Money Saved

Estimated Money Saved answers:

```text
How much money may this post have helped users avoid spending?
```

Formula:

```text
estimated_money_saved =
  saved_my_money_count * price_paid
```

This value is used by:

```text
GET /posts/{post_id}
GET /rankings/wallet-saved
```

### Buyer Regret Score v2

Buyer Regret Score v2 answers:

```text
How bad is this product failure, adjusted by community validation?
```

It uses:

```text
author_score
SAME_HERE
AGREE
DISAGREE
```

It does not use:

```text
SAVED_MY_MONEY
```

## Ranking Usage

### Buyer Regret Ranking

Buyer Regret ranking uses Buyer Regret Score v2 at read time.

Endpoint:

```text
GET /rankings/buyer-regret
```

Supported periods:

```text
week
month
all_time
```

Sorting:

```text
buyer_regret_score DESC
community_validation_count DESC
created_at DESC
```

The ranking response includes both the stored author score and the calculated v2 score:

```text
author_score
buyer_regret_score
calculation_version
same_here_count
agree_count
disagree_count
community_validation_count
```

### Wallet Saved Ranking

Wallet Saved ranking is separate from Buyer Regret ranking.

Endpoint:

```text
GET /rankings/wallet-saved
```

Formula:

```text
estimated_money_saved = saved_my_money_count * price_paid
```

Sorting:

```text
estimated_money_saved DESC
saved_my_money_count DESC
created_at DESC
```

`HELPFUL`, `SAME_HERE`, `AGREE`, and `DISAGREE` are not used by Wallet Saved ranking.

## Implemented Steps

1. Added `VerdictType` enum with `AGREE` and `DISAGREE`.
2. Added `PostVerdict` model.
3. Added Alembic migration for `post_verdicts`.
4. Added verdict request/response schemas.
5. Implemented `POST /posts/{post_id}/verdicts/{verdict_type}`.
6. Added verdict summary and `my_verdict` to post detail.
7. Added Buyer Regret Score v2 service functions.
8. Added focused service tests for smoothing, dynamic weight, and final score calculation.
9. Added `GET /rankings/buyer-regret`.
10. Added `GET /rankings/wallet-saved`.

## Calculation Version

```text
fail_score_v2
```

The existing v1 calculation version remains:

```text
fail_score_v1
```

## Resolved Implementation Decisions

- Buyer Regret Score v2 is calculated at read time for rankings instead of being stored in the database.
- The stored `ProductFailScore.final_score` remains the author score.
- `GET /rankings/buyer-regret` uses v2 immediately and explains the community validation counts in the response.
- `AGREE` and `DISAGREE` are shown in post detail through `verdict_summary` and `my_verdict`.
- `SAVED_MY_MONEY` is reserved for `estimated_money_saved` and Wallet Saved ranking.
