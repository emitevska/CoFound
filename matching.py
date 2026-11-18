
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# 1. LOAD THE DATASETS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

users = pd.read_csv(BASE_DIR / "data" / "user_profiles.csv")
projects = pd.read_csv(BASE_DIR / "data" / "projects.csv")

print("=== CoFound AI Collaborator Matching ===")

print("\n=== Dataset Summary ===")
print("Total users:", len(users))
print("Total projects:", len(projects))


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def split_items(value):
    """Convert comma-separated text into a set of lowercase values."""

    if pd.isna(value):
        return set()

    return {
        item.strip().lower()
        for item in str(value).split(",")
        if item.strip()
    }


def normalize_text(value):
    """Normalize text for simple category and role comparisons."""

    if pd.isna(value):
        return ""

    return str(value).strip().lower()


# ==========================================
# 3. SKILL MATCHING
# ==========================================

def calculate_skill_match(user_skills, required_skills):
    """
    Calculate the percentage of required skills
    that a candidate possesses.
    """

    user_set = split_items(user_skills)
    required_set = split_items(required_skills)

    if not required_set:
        return 0.0

    matching_skills = user_set.intersection(required_set)

    return len(matching_skills) / len(required_set)


# ==========================================
# 4. INTEREST MATCHING
# ==========================================

def calculate_interest_match(
    user_interests,
    preferred_project_types,
    project_category
):
    """
    Compare the project category with the user's
    interests and preferred project types.

    This is an exact category matching method.
    """

    interests = split_items(user_interests)
    preferred_types = split_items(preferred_project_types)
    categories = split_items(project_category)

    if not categories:
        return 0.0

    combined_preferences = interests.union(preferred_types)

    matching_categories = combined_preferences.intersection(categories)

    return len(matching_categories) / len(categories)


# ==========================================
# 5. AVAILABILITY MATCHING
# ==========================================

def calculate_availability_match(hours_available, hours_required):
    """
    Compare user availability with the project's
    required weekly commitment.

    Full score = enough available hours.
    Partial score = insufficient available hours.
    """

    try:
        available = float(hours_available)
        required = float(hours_required)

        if required <= 0:
            return 0.0

        return max(0.0, min(available / required, 1.0))

    except (ValueError, TypeError):
        return 0.0


# ==========================================
# 6. ROLE MATCHING
# ==========================================

def calculate_role_match(preferred_role, required_role):
    """
    Return 1 if the candidate's preferred role
    matches the project's required role.
    """

    user_role = normalize_text(preferred_role)
    project_role = normalize_text(required_role)

    if not user_role or not project_role:
        return 0.0

    return 1.0 if user_role == project_role else 0.0


# ==========================================
# 7. EXPERIENCE MATCHING
# ==========================================

def calculate_experience_match(user_experience, required_experience):
    """
    Check whether the candidate meets the
    project's minimum experience requirement.
    """

    levels = {
        "beginner": 1,
        "intermediate": 2,
        "advanced": 3
    }

    user_level = levels.get(normalize_text(user_experience), 0)
    required_level = levels.get(normalize_text(required_experience), 0)

    if user_level == 0 or required_level == 0:
        return 0.0

    return 1.0 if user_level >= required_level else 0.0


# ==========================================
# 8. COLLABORATION MODE MATCHING
# ==========================================

def calculate_collaboration_match(user_mode, project_mode):
    """
    Compare preferred collaboration modes.

    Exact match = 1.0
    Hybrid/On-site combination = 0.5
    Otherwise = 0.0

    These are prototype assumptions.
    """

    user_mode = normalize_text(user_mode)
    project_mode = normalize_text(project_mode)

    if not user_mode or not project_mode:
        return 0.0

    if user_mode == project_mode:
        return 1.0

    if {user_mode, project_mode} == {"hybrid", "on-site"}:
        return 0.5

    return 0.0


# ==========================================
# 9. RECOMMEND COLLABORATORS
# ==========================================

def recommend_collaborators(project_id, top_n=3, verbose=True):
    """
    Recommend the top candidates for a project
    using content-based matching and weighted ranking.
    """

    selected = projects[projects["project_id"] == project_id]

    if selected.empty:
        if verbose:
            print("Project not found:", project_id)
        return pd.DataFrame()

    project = selected.iloc[0]

    if verbose:
        print("\n===================================")
        print("Project:", project["title"])
        print("Description:", project["description"])
        print("Required Skills:", project["required_skills"])
        print("Required Role:", project["required_role"])
        print("Required Experience:", project["required_experience"])
        print("Hours per Week:", project["hours_per_week"])
        print("Collaboration Mode:", project["collaboration_mode"])
        print("Category:", project["category"])
        print("===================================")

    # ======================================
    # 10. PREPARE TEXT FOR TF-IDF
    # ======================================

    project_text = (
        str(project["description"]) + " " +
        str(project["required_skills"]) + " " +
        str(project["category"])
    )

    user_texts = (
        users["skills"].fillna("").astype(str) + " " +
        users["interests"].fillna("").astype(str) + " " +
        users["preferred_project_types"].fillna("").astype(str)
    ).tolist()

    all_texts = [project_text] + user_texts

    # ======================================
    # 11. TF-IDF VECTORIZATION
    # ======================================

    vectorizer = TfidfVectorizer(stop_words="english")

    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # ======================================
    # 12. COSINE SIMILARITY
    # ======================================

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    ).flatten()

    # ======================================
    # 13. CALCULATE MATCHING SCORES
    # ======================================

    results = users.copy()

    results["text_similarity"] = similarity_scores

    results["skill_match"] = results["skills"].apply(
        lambda skills: calculate_skill_match(
            skills,
            project["required_skills"]
        )
    )

    results["interest_match"] = results.apply(
        lambda user: calculate_interest_match(
            user["interests"],
            user["preferred_project_types"],
            project["category"]
        ),
        axis=1
    )

    results["availability_match"] = results["availability"].apply(
        lambda hours: calculate_availability_match(
            hours,
            project["hours_per_week"]
        )
    )

    results["role_match"] = results["preferred_role"].apply(
        lambda role: calculate_role_match(
            role,
            project["required_role"]
        )
    )

    results["experience_match"] = results["experience"].apply(
        lambda experience: calculate_experience_match(
            experience,
            project["required_experience"]
        )
    )

    results["collaboration_match"] = results["collaboration_mode"].apply(
        lambda mode: calculate_collaboration_match(
            mode,
            project["collaboration_mode"]
        )
    )

    # ======================================
    # 14. WEIGHTED MATCHING FORMULA
    # ======================================

    # Prototype weights:
    # 30% text similarity
    # 25% skill matching
    # 10% interest matching
    # 10% availability
    # 10% role matching
    # 10% experience matching
    #  5% collaboration compatibility
    #
    # Total = 100%
    #
    # These weights are design assumptions.
    # They must be evaluated against a baseline.

    results["final_score"] = (
        0.30 * results["text_similarity"] +
        0.25 * results["skill_match"] +
        0.10 * results["interest_match"] +
        0.10 * results["availability_match"] +
        0.10 * results["role_match"] +
        0.10 * results["experience_match"] +
        0.05 * results["collaboration_match"]
    )

    # Convert the weighted score to a 0-100 scale.
    # This is not a probability of success.

    results["match_score"] = (
        results["final_score"] * 100
    ).round(2)

    # ======================================
    # 15. FILTER AND RANK CANDIDATES
    # ======================================

    # Exclude candidates who have neither matching
    # required skills nor positive text similarity.

    results = results[
        (results["skill_match"] > 0) |
        (results["text_similarity"] > 0)
    ].copy()

    # Sort by final score.
    # User ID provides deterministic tie-breaking.

    results = results.sort_values(
        by=["final_score", "user_id"],
        ascending=[False, True]
    )

    top_results = results.head(top_n).copy()

    # ======================================
    # 16. DISPLAY RECOMMENDATIONS
    # ======================================

    if verbose:
        print("\n=== Top Collaborator Recommendations ===")

        if top_results.empty:
            print("No suitable collaborators found.")

        else:
            for rank, (_, user) in enumerate(
                top_results.iterrows(),
                start=1
            ):
                print(f"\n{rank}. {user['name']}")
                print("   User ID:", user["user_id"])
                print("   Skills:", user["skills"])
                print("   Preferred Role:", user["preferred_role"])
                print("   Experience:", user["experience"])
                print(
                    "   Availability:",
                    user["availability"],
                    "hours/week"
                )
                print(
                    "   Text Similarity:",
                    round(user["text_similarity"], 4)
                )
                print(
                    "   Skill Match:",
                    round(user["skill_match"] * 100, 2),
                    "%"
                )
                print(
                    "   Interest Match:",
                    round(user["interest_match"] * 100, 2),
                    "%"
                )
                print(
                    "   Availability Match:",
                    round(user["availability_match"] * 100, 2),
                    "%"
                )
                print(
                    "   Role Match:",
                    round(user["role_match"] * 100, 2),
                    "%"
                )
                print(
                    "   Experience Match:",
                    round(user["experience_match"] * 100, 2),
                    "%"
                )
                print(
                    "   Collaboration Match:",
                    round(user["collaboration_match"] * 100, 2),
                    "%"
                )
                print(
                    "   Final Match Score:",
                    user["match_score"],
                    "/ 100"
                )

    return top_results


# ==========================================
# 17. RUN RECOMMENDATIONS FOR ALL PROJECTS
# ==========================================

if __name__ == "__main__":

    for _, project in projects.iterrows():

        print(
            f"\n\n########## "
            f"{project['title'].upper()} "
            f"##########"
        )

        recommend_collaborators(project["project_id"])
