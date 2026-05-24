# Buyer Regret Score v2 Design

Status: Design Draft

This document describes the planned Buyer Regret Score v2 design for Amazn't. It is not implemented yet. The current implemented score is still Buyer Regret Score v1 in `app/services/product_fail_score_service.py`.

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
Wallet Saved Hall of Fame ranking
```

## Community Verdict Policy

Planned verdict types:

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

Planned endpoint:

```text
POST /posts/{post_id}/verdicts/{verdict_type}
```

Planned response shape:

```text
status: created | updated | deleted
post_id
verdict_type
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

## Planned Implementation Steps

1. Add `VerdictType` enum with `AGREE` and `DISAGREE`.
2. Add `PostVerdict` model.
3. Add Alembic migration for `post_verdicts`.
4. Add verdict request/response schemas.
5. Implement `POST /posts/{post_id}/verdicts/{verdict_type}`.
6. Add verdict summary and `my_verdict` to post detail.
7. Add Buyer Regret Score v2 service functions.
8. Add focused service tests for smoothing, dynamic weight, and final score calculation.

## Planned Calculation Version

```text
fail_score_v2
```

The existing v1 calculation version remains:

```text
fail_score_v1
```

## Open Implementation Questions

- Should Buyer Regret Score v2 be stored in the database or calculated at read time?
- Should v1 and v2 both be returned in post detail during the transition period?
- Should rankings use v2 immediately after implementation or after enough community data exists?
- Should `AGREE` / `DISAGREE` be shown in post detail before v2 ranking is enabled?
