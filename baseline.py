
import pandas as pd
from pathlib import Path


# ==========================================
# 1. LOAD THE DATASETS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

users = pd.read_csv(BASE_DIR / "data" / "user_profiles.csv")
projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")


# ==========================================
# 2. HELPER FUNCTION
# ==========================================

def split_items(value):
    """Convert comma-separated skills into lowercase values."""

    if pd.isna(value):
        return set()

    return {
        skill.strip().lower()
        for skill in str(value).split(",")
        if skill.strip()
    }


# ==========================================
# 3. CALCULATE SKILL OVERLAP
# ==========================================

def calculate_skill_overlap(user_skills, required_skills):
    """
    Calculate how many required skills a user has.

    Example:
    Required: Python, Machine Learning, Flask
    User: Python, Machine Learning, SQL

    Result: 2 / 3 = 0.6667
    """

    user_set = split_items(user_skills)
    required_set = split_items(required_skills)

    if not required_set:
        return 0.0

    matching_skills = user_set.intersection(required_set)

    return len(matching_skills) / len(required_set)


# ==========================================
# 4. BASELINE RECOMMENDATION FUNCTION
# ==========================================

def baseline_recommendations(project_id, top_n=3, verbose=True):
    """
    Recommend collaborators using only skill overlap.

    No TF-IDF or cosine similarity is used.
    """

    selected = projects[projects["project_id"] == project_id]

    if selected.empty:
        if verbose:
            print("Project not found:", project_id)
        return pd.DataFrame()

    project = selected.iloc[0]

    # Make a copy so the original dataset is unchanged.
    results = users.copy()

    # Calculate the skill overlap for every user.
    results["skill_overlap"] = results["skills"].apply(
        lambda skills: calculate_skill_overlap(
            skills,
            project["required_skills"]
        )
    )

    # Convert to a score between 0 and 100.
    results["baseline_score"] = (
        results["skill_overlap"] * 100
    ).round(2)

    # Exclude users without any required skills.
    results = results[
        results["skill_overlap"] > 0
    ].copy()

    # Rank by skill overlap.
    # Use user_id to break ties consistently.
    results = results.sort_values(
        by=["skill_overlap", "user_id"],
        ascending=[False, True]
    )

    top_results = results.head(top_n).copy()

    if verbose:
        print("\n===================================")
        print("Project:", project["title"])
        print("Required Skills:", project["required_skills"])
        print("===================================")

        print("\n=== Baseline Top Recommendations ===")

        if top_results.empty:
            print("No candidates with matching skills.")

        else:
            for rank, (_, user) in enumerate(
                top_results.iterrows(),
                start=1
            ):
                print(f"\n{rank}. {user['name']}")
                print("   User ID:", user["user_id"])
                print("   Skills:", user["skills"])
                print(
                    "   Skill Overlap:",
                    user["baseline_score"],
                    "%"
                )

    return top_results


# ==========================================
# 5. RUN BASELINE FOR ALL PROJECTS
# ==========================================

if __name__ == "__main__":

    print("=== CoFound Baseline Matching ===")

    print("\n=== Dataset Summary ===")
    print("Total users:", len(users))
    print("Total projects:", len(projects))

    for _, project in projects.iterrows():

        print(
            f"\n\n########## "
            f"{project['title'].upper()} "
            f"##########"
        )

        baseline_recommendations(project["project_id"])
