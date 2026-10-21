
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# 1. LOAD THE DATASETS
# ==========================================

users = pd.read_csv("data/user_profiles.csv")
projects = pd.read_csv("data/projects.csv")

print("=== CoFound AI Collaborator Matching ===")

print("\n=== Dataset Summary ===")
print("Total users:", len(users))
print("Total projects:", len(projects))


# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def split_items(value):
    """Convert comma-separated values into a set."""
    if pd.isna(value):
        return set()

    return {
        item.strip().lower()
        for item in str(value).split(",")
        if item.strip()
    }


def calculate_skill_match(user_skills, required_skills):
    """Calculate the proportion of required skills a user has."""

    user_set = split_items(user_skills)
    required_set = split_items(required_skills)

    if not required_set:
        return 0.0

    matching = user_set.intersection(required_set)

    return len(matching) / len(required_set)


def calculate_interest_match(user_interests, project_category):
    """Calculate simple keyword overlap between interests and category."""

    interests = split_items(user_interests)
    categories = split_items(project_category)

    if not categories:
        return 0.0

    matching = interests.intersection(categories)

    return len(matching) / len(categories)


def calculate_availability_match(hours_available):
    """
    Prototype assumption:
    10 or more hours per week gives full availability score.
    """

    try:
        hours = float(hours_available)
        return max(0.0, min(hours / 10.0, 1.0))
    except (ValueError, TypeError):
        return 0.0


# ==========================================
# 3. SELECT A PROJECT
# ==========================================

def recommend_collaborators(project_id, top_n=3):

    selected = projects[projects["project_id"] == project_id]

    if selected.empty:
        print("Project not found.")
        return pd.DataFrame()

    project = selected.iloc[0]

    print("\n===================================")
    print("Project:", project["title"])
    print("Description:", project["description"])
    print("Required Skills:", project["required_skills"])
    print("Category:", project["category"])
    print("===================================")

    # ======================================
    # 4. PREPARE TEXT FOR TF-IDF
    # ======================================

    project_text = (
        str(project["description"]) + " " +
        str(project["required_skills"]) + " " +
        str(project["category"])
    )

    user_texts = (
        users["skills"].fillna("").astype(str) + " " +
        users["interests"].fillna("").astype(str)
    ).tolist()

    all_texts = [project_text] + user_texts

    # ======================================
    # 5. TF-IDF VECTORIZATION
    # ======================================

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # ======================================
    # 6. COSINE SIMILARITY
    # ======================================

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    ).flatten()

    # ======================================
    # 7. CALCULATE MATCHING SCORES
    # ======================================

    results = users.copy()

    results["text_similarity"] = similarity_scores

    results["skill_match"] = results["skills"].apply(
        lambda skills: calculate_skill_match(
            skills,
            project["required_skills"]
        )
    )

    results["interest_match"] = results["interests"].apply(
        lambda interests: calculate_interest_match(
            interests,
            project["category"]
        )
    )

    results["availability_match"] = results["availability"].apply(
        calculate_availability_match
    )

    # ======================================
    # 8. WEIGHTED MATCHING FORMULA
    # ======================================

    # 50% text similarity
    # 30% skill matching
    # 10% interest matching
    # 10% availability

    results["final_score"] = (
        0.50 * results["text_similarity"] +
        0.30 * results["skill_match"] +
        0.10 * results["interest_match"] +
        0.10 * results["availability_match"]
    )

    # Convert final score to a 0-100 scale
    results["match_score"] = (
        results["final_score"] * 100
    ).round(2)

    # ======================================
    # 9. RANK COLLABORATORS
    # ======================================

    # Only recommend users with some text
    # similarity or matching required skills.

    results = results[
        (results["text_similarity"] > 0) |
        (results["skill_match"] > 0)
    ]

    results = results.sort_values(
        by="final_score",
        ascending=False
    )

    top_results = results.head(top_n)

    # ======================================
    # 10. DISPLAY RECOMMENDATIONS
    # ======================================

    print("\n=== Top Collaborator Recommendations ===")

    if top_results.empty:
        print("No suitable collaborators found.")
    else:
        for rank, (_, user) in enumerate(
            top_results.iterrows(), start=1
        ):
            print(f"\n{rank}. {user['name']}")
            print("   Skills:", user["skills"])
            print("   Interests:", user["interests"])
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
                "   Final Match Score:",
                user["match_score"],
                "/ 100"
            )

    return top_results


# ==========================================
# 11. RUN THE RECOMMENDATION SYSTEM
# ==========================================

print("\n\n########## FITTRACK ##########")
recommend_collaborators("P001")

print("\n\n########## SMARTSTUDY ##########")
recommend_collaborators("P002")
