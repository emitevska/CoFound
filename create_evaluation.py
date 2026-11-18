
import pandas as pd
from pathlib import Path

# ==========================================
# 1. LOAD DATASETS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

users = pd.read_csv(BASE_DIR / "data" / "user_profiles.csv")
projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def split_skills(value):
    """Convert comma-separated skills to a set."""

    if pd.isna(value):
        return set()

    return {
        skill.strip().lower()
        for skill in str(value).split(",")
        if skill.strip()
    }


def meets_experience(user_level, required_level):
    """Check whether experience meets the minimum."""

    levels = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    user = levels.get(str(user_level).strip().lower(), 0)
    required = levels.get(str(required_level).strip().lower(), 0)

    return user > 0 and required > 0 and user >= required


# ==========================================
# 3. CREATE EVALUATION LABELS
# ==========================================

evaluation_rows = []

for _, project in projects.iterrows():

    required_skills = split_skills(project["required_skills"])

    for _, user in users.iterrows():

        user_skills = split_skills(user["skills"])

        matching_count = len(
            user_skills.intersection(required_skills)
        )

        # At least 2 required skills must match.
        skills_ok = matching_count >= 2

        # User must meet the required experience.
        experience_ok = meets_experience(
            user["experience"],
            project["required_experience"]
        )

        # User must have enough weekly hours.
        availability_ok = (
            float(user["availability"]) >=
            float(project["hours_per_week"])
        )

        # Relevant only if all conditions are met.
        relevant = int(
            skills_ok and
            experience_ok and
            availability_ok
        )

        evaluation_rows.append({
            "project_id": project["project_id"],
            "user_id": user["user_id"],
            "relevant": relevant
        })


# ==========================================
# 4. SAVE EVALUATION DATASET
# ==========================================

evaluation = pd.DataFrame(evaluation_rows)

output_file = BASE_DIR / "data" / "evaluation_labels.csv"

evaluation.to_csv(output_file, index=False)

print("=== CoFound Evaluation Dataset ===")
print("Total project-user pairs:", len(evaluation))
print("Relevant pairs:", evaluation["relevant"].sum())
print("Not relevant pairs:", (evaluation["relevant"] == 0).sum())
print("Saved to:", output_file)

print("\nRelevant matches per project:")
print(
    evaluation.groupby("project_id")["relevant"].sum()
)
