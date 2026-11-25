import math
from pathlib import Path

import pandas as pd

from baseline import baseline_recommendations
from matching import recommend_collaborators


# 1. Load evaluation data

BASE_DIR = Path(__file__).resolve().parent

projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")
labels = pd.read_csv(BASE_DIR / "data" / "evaluation_labels.csv")

K = 3

METHODS = ["Baseline", "Original AI", "Improved AI"]


# 2. Evaluation metrics

def evaluate_top_k(recommended_ids, relevant_ids, k=3):
    """Calculate Precision@K and Recall@K."""

    recommended = list(recommended_ids)[:k]
    relevant = set(relevant_ids)

    correct = len(set(recommended) & relevant)

    precision = correct / k
    recall = correct / len(relevant) if relevant else None

    return precision, recall


def reciprocal_rank(recommended_ids, relevant_ids):
    """Calculate the reciprocal rank of the first relevant result."""

    relevant = set(relevant_ids)

    for rank, user_id in enumerate(recommended_ids, start=1):
        if user_id in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(recommended_ids, relevant_ids, k=3):
    """Calculate ranking quality using NDCG@K."""

    relevant = set(relevant_ids)

    if not relevant:
        return None

    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, user_id in enumerate(recommended_ids[:k], start=1)
        if user_id in relevant
    )

    ideal_count = min(len(relevant), k)

    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_count + 1)
    )

    return dcg / idcg


# 3. Compare all three matching methods

comparison_rows = []

for _, project in projects.iterrows():

    project_id = project["project_id"]

    project_labels = labels[labels["project_id"] == project_id]

    relevant_ids = set(
        project_labels[project_labels["relevant"] == 1]["user_id"]
    )

    # Method 1: Skill overlap only
    baseline_results = baseline_recommendations(
        project_id,
        top_n=K,
        verbose=False
    )

    # Method 2: AI without mandatory filters
    original_ai_results = recommend_collaborators(
        project_id,
        top_n=K,
        verbose=False,
        mandatory_filters=False
    )

    # Method 3: AI with mandatory filters
    improved_ai_results = recommend_collaborators(
        project_id,
        top_n=K,
        verbose=False,
        mandatory_filters=True
    )

    methods = [
        ("Baseline", baseline_results),
        ("Original AI", original_ai_results),
        ("Improved AI", improved_ai_results)
    ]

    for method, results in methods:

        recommended_ids = results["user_id"].tolist()[:K]

        total_recommended = len(recommended_ids)

        valid_recommendations = sum(
            user_id in relevant_ids
            for user_id in recommended_ids
        )

        invalid_recommendations = (
            total_recommended - valid_recommendations
        )

        precision, recall = evaluate_top_k(
            recommended_ids, relevant_ids, K
        )

        mrr_score = reciprocal_rank(
            recommended_ids, relevant_ids
        )

        ndcg_score = ndcg_at_k(
            recommended_ids, relevant_ids, K
        )

        comparison_rows.append({
            "project_id": project_id,
            "project": project["title"],
            "method": method,
            "relevant_candidates": len(relevant_ids),
            "recommendations": total_recommended,
            "valid_recommendations": valid_recommendations,
            "invalid_recommendations": invalid_recommendations,
            "precision_at_3": precision,
            "recall_at_3": recall,
            "mrr": mrr_score,
            "ndcg_at_3": ndcg_score
        })


# 4. Create detailed comparison dataset

comparison = pd.DataFrame(comparison_rows)

eligible = comparison[
    comparison["relevant_candidates"] > 0
].copy()


# 5. Calculate average evaluation metrics

summary = pd.DataFrame({
    "Precision@3": comparison.groupby("method")[
        "precision_at_3"
    ].mean(),

    "Recall@3": eligible.groupby("method")[
        "recall_at_3"
    ].mean(),

    "MRR": comparison.groupby("method")[
        "mrr"
    ].mean(),

    "NDCG@3": eligible.groupby("method")[
        "ndcg_at_3"
    ].mean()
})

summary = summary.reindex(METHODS)


# 6. Calculate recommendation quality and coverage

quality_rows = []

for method in METHODS:

    method_results = comparison[
        comparison["method"] == method
    ]

    total = method_results["recommendations"].sum()
    valid = method_results["valid_recommendations"].sum()
    invalid = method_results["invalid_recommendations"].sum()

    validity = valid / total * 100 if total else None

    covered_projects = (
        method_results["recommendations"] > 0
    ).sum()

    coverage = covered_projects / len(projects) * 100

    quality_rows.append({
        "Method": method,
        "Total recommendations": total,
        "Valid recommendations": valid,
        "Invalid recommendations": invalid,
        "Validity (%)": validity,
        "Projects covered": covered_projects,
        "Coverage (%)": coverage
    })

quality = pd.DataFrame(quality_rows).set_index("Method")


# 7. Display experiment results

print("\n=== CoFound Matching Experiment ===")

print("\n=== Dataset Summary ===")
print("Total projects:", len(projects))
print("Total evaluation pairs:", len(labels))
print("Total relevant pairs:", int(labels["relevant"].sum()))

print("\n=== Precision@3 by Project ===")

print(
    comparison.pivot(
        index="project",
        columns="method",
        values="precision_at_3"
    ).reindex(columns=METHODS).round(3).to_string()
)

print("\n=== Final Method Comparison ===")
print(summary.round(3).to_string())

print("\n=== Recommendation Quality ===")
print(quality.round(2).to_string())

print("\n=== Projects Without Relevant Candidates ===")

no_relevant_projects = comparison[
    comparison["relevant_candidates"] == 0
]["project"].drop_duplicates().tolist()

print(no_relevant_projects)

print("\n=== Evaluation Notes ===")
print("Precision@3 uses a fixed denominator of 3.")
print("MRR is calculated over the returned top 3 results.")
print("Recall and NDCG exclude projects with no relevant candidates.")
print("Relevance labels are generated using mandatory eligibility rules.")
print("Results measure rule-based eligibility, not real-world success.")


# 8. Save experiment results

output_file = BASE_DIR / "data" / "comparison_results.csv"

experiments_dir = BASE_DIR / "experiments"
experiments_dir.mkdir(parents=True, exist_ok=True)

summary_file = experiments_dir / "experiment_summary.csv"
quality_file = experiments_dir / "recommendation_quality.csv"

comparison.to_csv(output_file, index=False)
summary.round(4).to_csv(summary_file)
quality.round(4).to_csv(quality_file)

print("\n=== Experiment Files Saved ===")
print("Detailed results:", output_file)
print("Summary results:", summary_file)
print("Recommendation quality:", quality_file)