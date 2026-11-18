
# CoFound – Week 9 Experiment

## 1. Objective

The goal of this experiment was to compare our AI
collaborator matching algorithm with a simple baseline
and check which method recommends better candidates.

## 2. Dataset

We used a synthetic dataset containing:
- 40 user profiles
- 10 projects
- 400 project-user combinations

Based on our evaluation rules, 11 combinations
were labeled as relevant.

## 3. Methods

### Baseline
The baseline recommends candidates based only on
how many required project skills they have.

### AI Matching
Our AI algorithm uses TF-IDF, cosine similarity,
and a weighted score based on skills, interests,
availability, preferred role, experience,
and collaboration mode.

## 4. Evaluation

We used four metrics:
- Precision@3: How many of the top 3 are relevant.
- Recall@3: How many relevant candidates were found.
- MRR: How high the first relevant candidate appears.
- NDCG@3: How well relevant candidates are ranked.

## 5. Results

| Metric | Baseline | AI Matching |
|---|---|---|
| Precision@3 | 0.333 | 0.333 |
| Recall@3 | 0.944 | 0.944 |
| MRR | 0.433 | 0.550 |
| NDCG@3 | 0.787 | 0.908 |

## 6. Interpretation

Both methods found the same number of relevant
candidates in their top 3 recommendations.

However, the AI algorithm achieved better MRR
and NDCG@3 scores. This means it generally placed
relevant candidates higher in the ranking.

## 7. Limitations

The dataset is synthetic, and relevance labels
were automatically generated using skill,
experience, and availability requirements.

Four projects had no relevant candidates under
these rules.

The results are preliminary and do not prove
that the AI method will perform better with
real users.

## 8. Conclusion

Our AI matching method showed better ranking
quality than the baseline in this experiment,
although both methods had the same Precision@3
and Recall@3.

Future testing should include independently
reviewed relevance labels and more realistic data.


## 9. Error Analysis

We analyzed the top 3 recommendations from both
methods to understand why some candidates were
not suitable for the projects.

The baseline produced 19 non-relevant
recommendations, while AI Matching produced 20.

The main problems were:
- Candidates did not have enough matching skills.
- Candidates had less experience than required.
- Candidates did not have enough available hours.

For example, one candidate recommended for
ShopEase had matching skills but not enough
available hours.

These results show that skill matching alone
is not enough to find suitable collaborators.

Our AI algorithm considers more information,
but it can still recommend candidates who
do not meet all project requirements.

In the future, we could improve the system by
filtering candidates who do not meet mandatory
requirements before ranking them.

## 10. Future Improvements

Possible improvements include:
- Adding mandatory requirement filters.
- Testing with real or independently reviewed data.
- Improving the scoring weights.
- Evaluating recommendations on more projects.
- Considering location and project preferences.
