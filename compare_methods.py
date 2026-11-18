
import math
from pathlib import Path

import pandas as pd

from baseline import baseline_recommendations
from matching import recommend_collaborators


# ==========================================
# 1. LOAD EVALUATION DATA
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")
labels = pd.read_csv(BASE_DIR / "data" / "evaluation_labels.csv")


# ==========================================
# 2. PRECISION@K AND RECALL@K
# ==========================================

def evaluate_top_k(recommended_ids, relevant_ids, k=3):
    """
    Calculate Precision@K and Recall@K.

    Precision@K:
    How many of the top K recommendations are relevant?

    Recall@K:
    How many of all relevant candidates were found?

    Projects without relevant candidates have
    undefined recall (None).
    """

    recommended = list(recommended_ids)[:k]
    relevant = set(relevant_ids)

    correct = len(set(recommended).intersection(relevant))

    precision = correct / k

    recall = (
        correct / len(relevant)
        if relevant else None
    )

    return precision, recall


# ==========================================
# 3. RECIPROCAL RANK
# ==========================================

def reciprocal_rank(recommended_ids, relevant_ids):
    """
    Calculate the reciprocal rank of the first
    relevant candidate.

    Rank 1 -> 1.0
    Rank 2 -> 0.5
    Rank 3 -> 0.3333

    No relevant candidate -> 0.0

    Mean Reciprocal Rank (MRR) is calculated
    by averaging reciprocal ranks.
    """

    relevant = set(relevant_ids)

    for rank, user_id in enumerate(recommended_ids, start=1):

        if user_id in relevant:
            return 1.0 / rank

    return 0.0


# ==========================================
# 4. NDCG@K
# ==========================================

def ndcg_at_k(recommended_ids, relevant_ids, k=3):
    """
    Calculate Normalized Discounted Cumulative Gain.

    Relevant candidates receive a relevance of 1.
    Non-relevant candidates receive a relevance of 0.

    Relevant candidates appearing higher in the
    ranking contribute more to the score.

    Projects with no relevant candidates return None.
    """

    relevant = set(relevant_ids)

    if not relevant:
        return None

    # Calculate actual Discounted Cumulative Gain.
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, user_id in enumerate(
            list(recommended_ids)[:k],
            start=1
        )
        if user_id in relevant
    )

    # Calculate the ideal ranking score.
    ideal_count = min(len(relevant), k)

    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_count + 1)
    )

    # Normalize the actual score.
    return dcg / idcg


# ==========================================
# 5. COMPARE BASELINE AND AI METHODS
# ==========================================

comparison_rows = []

for _, project in projects.iterrows():

    project_id = project["project_id"]

    # Get the evaluation labels for this project.
    project_labels = labels[
        labels["project_id"] == project_id
    ]

    # Get all candidates labeled as relevant.
    relevant_ids = set(
        project_labels[
            project_labels["relevant"] == 1
        ]["user_id"]
    )

    # --------------------------------------
    # BASELINE: SKILL OVERLAP ONLY
    # --------------------------------------

    baseline_results = baseline_recommendations(
        project_id,
        top_n=3,
        verbose=False
    )

    # --------------------------------------
    # AI: TF-IDF + WEIGHTED MATCHING
    # --------------------------------------

    ai_results = recommend_collaborators(
        project_id,
        top_n=3,
        verbose=False
    )

    # --------------------------------------
    # EVALUATE BOTH METHODS
    # --------------------------------------

    for method, results in [
        ("Baseline", baseline_results),
        ("AI Matching", ai_results)
    ]:

        recommended_ids = results["user_id"].tolist()

        # Precision@3 and Recall@3
        precision, recall = evaluate_top_k(
            recommended_ids,
            relevant_ids,
            k=3
        )

        # Reciprocal Rank
        mrr_score = reciprocal_rank(
            recommended_ids,
            relevant_ids
        )

        # NDCG@3
        ndcg_score = ndcg_at_k(
            recommended_ids,
            relevant_ids,
            k=3
        )

        # Store experiment results.
        comparison_rows.append({
            "project_id": project_id,
            "project": project["title"],
            "method": method,
            "relevant_candidates": len(relevant_ids),
            "precision_at_3": precision,
            "recall_at_3": recall,
            "mrr": mrr_score,
            "ndcg_at_3": ndcg_score
        })


# ==========================================
# 6. CREATE COMPARISON DATAFRAME
# ==========================================

comparison = pd.DataFrame(comparison_rows)

# Only projects with at least one relevant
# candidate have defined Recall and NDCG.

eligible = comparison[
    comparison["relevant_candidates"] > 0
].copy()


# ==========================================
# 7. DISPLAY EXPERIMENT RESULTS
# ==========================================

print("\n=== CoFound Week 9 Experiment ===")

print("\n=== Dataset Summary ===")
print("Total projects:", len(projects))
print("Total evaluation pairs:", len(labels))
print("Total relevant pairs:", int(labels["relevant"].sum()))

# ------------------------------------------
# PRECISION@3 BY PROJECT
# ------------------------------------------

print("\n=== Precision@3 by Project ===")

print(
    comparison.pivot(
        index="project",
        columns="method",
        values="precision_at_3"
    ).round(3).to_string()
)

# ------------------------------------------
# AVERAGE PRECISION@3
# ------------------------------------------

print("\n=== Average Precision@3 ===")

print(
    comparison.groupby("method")[
        "precision_at_3"
    ].mean().round(3)
)

# ------------------------------------------
# AVERAGE RECALL@3
# ------------------------------------------

print("\n=== Average Recall@3 ===")

print(
    eligible.groupby("method")[
        "recall_at_3"
    ].mean().round(3)
)

# ------------------------------------------
# MEAN RECIPROCAL RANK
# ------------------------------------------

print("\n=== Mean Reciprocal Rank (MRR) ===")

print(
    comparison.groupby("method")[
        "mrr"
    ].mean().round(3)
)

# ------------------------------------------
# AVERAGE NDCG@3
# ------------------------------------------

print("\n=== Average NDCG@3 ===")

print(
    eligible.groupby("method")[
        "ndcg_at_3"
    ].mean().round(3)
)

# ------------------------------------------
# PROJECTS WITHOUT RELEVANT CANDIDATES
# ------------------------------------------

print("\n=== Projects With No Relevant Candidates ===")

no_relevant_projects = comparison[
    comparison["relevant_candidates"] == 0
]["project"].drop_duplicates().tolist()

print(no_relevant_projects)


# ==========================================
# 8. DISPLAY FINAL COMPARISON TABLE
# ==========================================

print("\n=== Final Method Comparison ===")

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

print(summary.round(3).to_string())


# ==========================================
# 9. SAVE EXPERIMENT RESULTS
# ==========================================

# Save detailed results for all 10 projects.
output_file = BASE_DIR / "data" / "comparison_results.csv"

comparison.to_csv(output_file, index=False)

# Save the average results for each method.
summary_file = BASE_DIR / "experiments" / "experiment_summary.csv"

summary_file.parent.mkdir(parents=True, exist_ok=True)

summary.round(4).to_csv(summary_file)

print("\n=== Experiment Files Saved ===")
print("Detailed results:", output_file)
print("Summary results:", summary_file)
