
import pandas as pd
from pathlib import Path

from baseline import baseline_recommendations
from matching import recommend_collaborators


BASE_DIR = Path(__file__).resolve().parent

users = pd.read_csv(BASE_DIR / "data" / "user_profiles.csv")
projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")
labels = pd.read_csv(BASE_DIR / "data" / "evaluation_labels.csv")


def get_error_reasons(user, project):
    reasons = []

    required_skills = {
        skill.strip().lower()
        for skill in str(project["required_skills"]).split(",")
    }

    user_skills = {
        skill.strip().lower()
        for skill in str(user["skills"]).split(",")
    }

    matching_skills = len(required_skills & user_skills)

    if matching_skills < 2:
        reasons.append("Not enough matching skills")

    levels = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    user_level = levels.get(
        str(user["experience"]).strip().lower(), 0
    )

    required_level = levels.get(
        str(project["required_experience"]).strip().lower(), 0
    )

    if user_level < required_level:
        reasons.append("Experience below requirement")

    if float(user["availability"]) < float(project["hours_per_week"]):
        reasons.append("Not enough available hours")

    return reasons


errors = []

for _, project in projects.iterrows():

    project_id = project["project_id"]

    recommendations = {
        "Baseline": baseline_recommendations(
            project_id, top_n=3, verbose=False
        ),
        "AI Matching": recommend_collaborators(
            project_id, top_n=3, verbose=False
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
                continue

            if int(label_row.iloc[0]["relevant"]) == 0:

                user = users[
                    users["user_id"] == user_id
                ].iloc[0]

                reasons = get_error_reasons(user, project)

                errors.append({
                    "project_id": project_id,
                    "project": project["title"],
                    "method": method,
                    "rank": rank,
                    "user_id": user_id,
                    "candidate": user["name"],
                    "error_reasons": "; ".join(reasons)
                })


errors_df = pd.DataFrame(errors)

output_file = (
    BASE_DIR / "experiments" / "error_analysis.csv"
)

errors_df.to_csv(output_file, index=False)

print("\n=== CoFound Week 9 Error Analysis ===")

print("\nTotal non-relevant recommendations:", len(errors_df))

print("\nNon-relevant recommendations by method:")
print(errors_df.groupby("method").size())

print("\nExamples of recommendation errors:")

for _, error in errors_df.head(10).iterrows():
    print(
        f"{error['method']} | "
        f"{error['project']} | "
        f"Rank {error['rank']} | "
        f"{error['candidate']} | "
        f"{error['error_reasons']}"
    )

print("\nSaved to:", output_file)

