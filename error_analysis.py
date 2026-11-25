import pandas as pd
from pathlib import Path

from baseline import baseline_recommendations
from matching import recommend_collaborators


# 1. Load datasets

BASE_DIR = Path(__file__).resolve().parent

users = pd.read_csv(BASE_DIR / "data" / "user_profiles.csv")
projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")
labels = pd.read_csv(BASE_DIR / "data" / "evaluation_labels.csv")

METHODS = ["Baseline", "Original AI", "Improved AI"]


# 2. Identify failed requirements

def get_error_reasons(label):

    reasons = []

    if label["skills_ok"] == 0:
        reasons.append("Not enough matching skills")

    if label["experience_ok"] == 0:
        reasons.append("Experience below requirement")

    if label["availability_ok"] == 0:
        reasons.append("Not enough available hours")

    return reasons


# 3. Analyze recommendations

errors = []

for _, project in projects.iterrows():

    project_id = project["project_id"]

    recommendations = {
        "Baseline": baseline_recommendations(
            project_id,
            top_n=3,
            verbose=False
        ),

        "Original AI": recommend_collaborators(
            project_id,
            top_n=3,
            verbose=False,
            mandatory_filters=False
        ),

        "Improved AI": recommend_collaborators(
            project_id,
            top_n=3,
            verbose=False,
            mandatory_filters=True
        )
    }

    for method, results in recommendations.items():

        for rank, (_, candidate) in enumerate(
            results.iterrows(), start=1
        ):

            user_id = candidate["user_id"]

            label_row = labels[
                (labels["project_id"] == project_id)
                & (labels["user_id"] == user_id)
            ]

            if label_row.empty:
                raise ValueError(
                    f"Missing label: {project_id}, {user_id}"
                )

            label = label_row.iloc[0]

            if int(label["relevant"]) == 0:

                user = users[
                    users["user_id"] == user_id
                ].iloc[0]

                reasons = get_error_reasons(label)

                errors.append({
                    "project_id": project_id,
                    "project": project["title"],
                    "method": method,
                    "rank": rank,
                    "user_id": user_id,
                    "candidate": user["name"],
                    "skills_failed": int(label["skills_ok"] == 0),
                    "experience_failed": int(label["experience_ok"] == 0),
                    "availability_failed": int(label["availability_ok"] == 0),
                    "error_reasons": "; ".join(reasons)
                })


# 4. Create error analysis dataset

columns = [
    "project_id", "project", "method", "rank",
    "user_id", "candidate", "skills_failed",
    "experience_failed", "availability_failed",
    "error_reasons"
]

errors_df = pd.DataFrame(errors, columns=columns)


# 5. Summarize errors by method

summary_rows = []

for method in METHODS:

    method_errors = errors_df[
        errors_df["method"] == method
    ]

    summary_rows.append({
        "Method": method,
        "Invalid recommendations": len(method_errors),
        "Insufficient skills": method_errors["skills_failed"].sum(),
        "Insufficient experience": method_errors["experience_failed"].sum(),
        "Insufficient availability": method_errors["availability_failed"].sum()
    })

summary = pd.DataFrame(summary_rows).set_index("Method")


# 6. Display results

print("\n=== CoFound Error Analysis ===")

print("\nTotal invalid recommendations:", len(errors_df))

print("\n=== Error Summary by Method ===")
print(summary.to_string())

print("\n=== Examples of Recommendation Errors ===")

for method in METHODS:

    print(f"\n{method}:")

    examples = errors_df[
        errors_df["method"] == method
    ].head(5)

    if examples.empty:
        print("No invalid recommendations found.")

    else:
        for _, error in examples.iterrows():
            print(
                f"{error['project']} | "
                f"Rank {error['rank']} | "
                f"{error['candidate']} | "
                f"{error['error_reasons']}"
            )

print("\nNote: One recommendation may fail multiple requirements.")


# 7. Save results

experiments_dir = BASE_DIR / "experiments"
experiments_dir.mkdir(parents=True, exist_ok=True)

output_file = experiments_dir / "error_analysis.csv"
summary_file = experiments_dir / "error_summary.csv"

errors_df.to_csv(output_file, index=False)
summary.to_csv(summary_file)

print("\n=== Files Saved ===")
print("Detailed errors:", output_file)
print("Error summary:", summary_file)