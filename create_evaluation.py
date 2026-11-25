import pandas as pd
from pathlib import Path

# 1. Load datasets

BASE_DIR = Path(__file__).resolve().parent

users = pd.read_csv(BASE_DIR / "data" / "user_profiles.csv")
projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")


# 2. Helper functions

def split_skills(value):
    """Convert comma-separated skills into a set."""
    if pd.isna(value):
        return set()

    return {
        skill.strip().lower()
        for skill in str(value).split(",")
        if skill.strip()
    }


def meets_experience(user_level, required_level):
    """Check whether the user meets the minimum experience."""

    levels = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    user = levels.get(str(user_level).strip().lower(), 0)
    required = levels.get(str(required_level).strip().lower(), 0)

    return user > 0 and required > 0 and user >= required


# 3. Generate rule-based evaluation labels

evaluation_rows = []

for _, project in projects.iterrows():

    required_skills = split_skills(project["required_skills"])
    minimum_skills = min(2, len(required_skills))

    for _, user in users.iterrows():

        user_skills = split_skills(user["skills"])
        matching_count = len(user_skills & required_skills)

        # Check mandatory requirements
        skills_ok = bool(required_skills) and matching_count >= minimum_skills

        experience_ok = meets_experience(
            user["experience"],
            project["required_experience"]
        )

        user_hours = float(user["availability"])
        required_hours = float(project["hours_per_week"])

        availability_ok = (
            required_hours > 0 and user_hours >= required_hours
        )

        # A pair is relevant when all requirements are satisfied
        relevant = int(
            skills_ok and experience_ok and availability_ok
        )

        evaluation_rows.append({
            "project_id": project["project_id"],
            "user_id": user["user_id"],
            "matched_skills": matching_count,
            "skills_ok": int(skills_ok),
            "experience_ok": int(experience_ok),
            "availability_ok": int(availability_ok),
            "relevant": relevant
        })


# 4. Save evaluation dataset

evaluation = pd.DataFrame(evaluation_rows)

output_file = BASE_DIR / "data" / "evaluation_labels.csv"
evaluation.to_csv(output_file, index=False)


# 5. Calculate evaluation statistics

total_pairs = len(evaluation)
relevant_pairs = evaluation["relevant"].sum()
non_relevant_pairs = total_pairs - relevant_pairs

relevance_percentage = (
    relevant_pairs / total_pairs * 100 if total_pairs else 0
)

matches_per_project = evaluation.groupby("project_id")["relevant"].sum()

projects_with_matches = (matches_per_project > 0).sum()
projects_without_matches = (matches_per_project == 0).sum()

coverage = (
    projects_with_matches / len(projects) * 100
    if len(projects) else 0
)


# 6. Display results

print("=== CoFound Evaluation Dataset ===")

print("\nDataset:")
print("Total users:", len(users))
print("Total projects:", len(projects))
print("Total project-user pairs:", total_pairs)

print("\nRelevance statistics:")
print("Relevant pairs:", relevant_pairs)
print("Not relevant pairs:", non_relevant_pairs)
print(f"Relevant pairs percentage: {relevance_percentage:.2f}%")

print("\nProject coverage:")
print("Projects with eligible collaborators:", projects_with_matches)
print("Projects without eligible collaborators:", projects_without_matches)
print(f"Project coverage: {coverage:.2f}%")

print("\nRelevant matches per project:")
print(matches_per_project.to_string())

print("\nSaved to:", output_file)