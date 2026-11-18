
import pandas as pd
from pathlib import Path

# Paths to the original and expanded datasets
original_file = Path("data/original/user_profiles.csv")
output_file = Path("data/user_profiles.csv")

# Load the original five users
users = pd.read_csv(original_file)

print("=== CoFound Dataset Expansion ===")
print("Original users:", len(users))
print("\nOriginal columns:")
print(users.columns.tolist())


# Add new attributes to the original five users

additional_data = {
    "preferred_role": [
        "UI/UX Designer",
        "Mobile Developer",
        "AI Developer",
        "Backend Developer",
        "Frontend Developer"
    ],
    "preferred_project_types": [
        "Mobile Apps, Design",
        "Mobile Apps, Health Tech",
        "AI, Education",
        "Backend, Databases",
        "Web Development, Design"
    ],
    "collaboration_mode": [
        "Remote",
        "Hybrid",
        "Remote",
        "Hybrid",
        "Remote"
    ],
    "location": [
        "Tetovo",
        "Skopje",
        "Tetovo",
        "Skopje",
        "Bitola"
    ]
}

# Assign the new columns to existing users
for column, values in additional_data.items():
    users[column] = values

print("\nUpdated columns:")
print(users.columns.tolist())

print("\nUpdated user profiles:")
print(users.to_string(index=False))


# Define the roles for the additional synthetic users

roles = [
    "AI Developer",
    "Frontend Developer",
    "Backend Developer",
    "Mobile Developer",
    "UI/UX Designer",
    "Data Scientist",
    "Cybersecurity / DevOps"
]

# Five new users for each role
profiles_per_role = 5

print("\n=== Dataset Expansion Plan ===")

for role in roles:
    print(f"{role}: {profiles_per_role} new users")

print("\nTotal planned users:",
      len(users) + len(roles) * profiles_per_role)


# Skill combinations for each role
# Each role has five different profiles

role_skills = {
    "AI Developer": [
        "Python, Machine Learning, TensorFlow",
        "Python, NLP, Scikit-learn",
        "Python, Deep Learning, PyTorch",
        "Python, Computer Vision, OpenCV",
        "Python, Machine Learning, Flask"
    ],
    "Frontend Developer": [
        "HTML, CSS, JavaScript",
        "JavaScript, React, CSS",
        "TypeScript, React, Tailwind CSS",
        "JavaScript, Vue, HTML",
        "React, Next.js, TypeScript"
    ],
    "Backend Developer": [
        "Python, Django, PostgreSQL",
        "Java, Spring Boot, SQL",
        "Node.js, Express, MongoDB",
        "Python, FastAPI, SQL",
        "C#, ASP.NET, SQL Server"
    ],
    "Mobile Developer": [
        "Kotlin, Android, Firebase",
        "Swift, iOS, SwiftUI",
        "Flutter, Dart, Firebase",
        "React Native, JavaScript, Firebase",
        "Kotlin, Java, Android"
    ],
    "UI/UX Designer": [
        "Figma, UI/UX, Prototyping",
        "Figma, Wireframing, User Research",
        "Adobe XD, UI Design, Prototyping",
        "Figma, Design Systems, UX Research",
        "UI/UX, Figma, Usability Testing"
    ],
    "Data Scientist": [
        "Python, Pandas, SQL",
        "Python, Data Analysis, Scikit-learn",
        "R, Statistics, Data Visualization",
        "Python, SQL, Power BI",
        "Python, Pandas, Tableau"
    ],
    "Cybersecurity / DevOps": [
        "Linux, Docker, AWS",
        "Cybersecurity, Network Security, Python",
        "Docker, Kubernetes, CI/CD",
        "AWS, Terraform, Linux",
        "Network Security, Linux, Penetration Testing"
    ]
}

print("\n=== Skill Profiles ===")

for role, skills in role_skills.items():
    print(f"{role}: {len(skills)} skill combinations")

print("Total new skill profiles:",
      sum(len(skills) for skills in role_skills.values()))


# Generate 35 synthetic user profiles

role_details = {
    "AI Developer": ("AI, Machine Learning", "AI, Education"),
    "Frontend Developer": ("Web Design, Frontend", "Web Development, Design"),
    "Backend Developer": ("Backend, Databases", "Web Development, Business"),
    "Mobile Developer": ("Mobile Apps, Technology", "Mobile Apps, Health Tech"),
    "UI/UX Designer": ("Design, User Experience", "Mobile Apps, Design"),
    "Data Scientist": ("Data Science, Analytics", "AI, Business"),
    "Cybersecurity / DevOps": ("Cybersecurity, Cloud", "Security, Technology")
}

experience_levels = [
    "Beginner", "Intermediate", "Advanced",
    "Intermediate", "Advanced"
]

availability_hours = [5, 8, 10, 12, 15]
collaboration_modes = ["Remote", "Hybrid", "On-site", "Remote", "Hybrid"]
locations = ["Tetovo", "Skopje", "Bitola", "Ohrid", "Gostivar"]

new_profiles = []
user_number = 6

for role, skill_sets in role_skills.items():
    interests, project_types = role_details[role]

    for i, skills in enumerate(skill_sets):
        new_profiles.append({
            "user_id": f"U{user_number:03d}",
            "name": f"Synthetic User {user_number:03d}",
            "skills": skills,
            "interests": interests,
            "experience": experience_levels[i],
            "availability": availability_hours[i],
            "preferred_role": role,
            "preferred_project_types": project_types,
            "collaboration_mode": collaboration_modes[i],
            "location": locations[i]
        })

        user_number += 1

# Combine original and new users
new_users = pd.DataFrame(new_profiles)
expanded_users = pd.concat([users, new_users], ignore_index=True)

print("\n=== Expanded User Dataset ===")
print("Total users:", len(expanded_users))
print("Total columns:", len(expanded_users.columns))
print("Duplicate IDs:", expanded_users["user_id"].duplicated().sum())


# Validate the expanded dataset before saving

required_columns = [
    "user_id", "name", "skills", "interests",
    "experience", "availability", "preferred_role",
    "preferred_project_types", "collaboration_mode",
    "location"
]

missing_columns = [
    col for col in required_columns
    if col not in expanded_users.columns
]

missing_values = expanded_users[required_columns].isna().sum().sum()
duplicate_ids = expanded_users["user_id"].duplicated().sum()

if missing_columns or missing_values or duplicate_ids:
    raise ValueError(
        f"Validation failed: missing columns={missing_columns}, "
        f"missing values={missing_values}, duplicate IDs={duplicate_ids}"
    )

if len(expanded_users) != 40:
    raise ValueError("Expected exactly 40 user profiles.")

# Save the validated dataset
expanded_users.to_csv(output_file, index=False)

print("\n=== Dataset Saved Successfully ===")
print("File:", output_file)
print("Users:", len(expanded_users))
print("Columns:", len(expanded_users.columns))
print("Missing values:", missing_values)
print("Duplicate IDs:", duplicate_ids)


# ==========================================
# EXPAND PROJECT DATASET
# ==========================================

# Load the original two projects
original_projects_file = Path("data/original/projects.csv")
projects_output_file = Path("data/projects.csv")

projects = pd.read_csv(original_projects_file)

print("\n=== Original Projects ===")
print("Total projects:", len(projects))
print("Columns:", projects.columns.tolist())


# Add new attributes to the original two projects

project_details = {
    "P001": {
        "required_role": "Mobile Developer",
        "required_experience": "Intermediate",
        "hours_per_week": 10,
        "collaboration_mode": "Remote",
        "location": "Skopje"
    },
    "P002": {
        "required_role": "AI Developer",
        "required_experience": "Intermediate",
        "hours_per_week": 8,
        "collaboration_mode": "Remote",
        "location": "Tetovo"
    }
}

# Assign project requirements using project IDs
for column in [
    "required_role",
    "required_experience",
    "hours_per_week",
    "collaboration_mode",
    "location"
]:
    projects[column] = projects["project_id"].map(
        lambda project_id: project_details[project_id][column]
    )

print("\n=== Updated Projects ===")
print("Total projects:", len(projects))
print("Total columns:", len(projects.columns))
print(projects.to_string(index=False))


# Create 8 additional fictional projects

new_projects = [
    {
        "project_id": "P003",
        "title": "ShopEase",
        "description": "E-commerce website for small businesses",
        "required_skills": "React, JavaScript, CSS",
        "category": "Web Development",
        "required_role": "Frontend Developer",
        "required_experience": "Intermediate",
        "hours_per_week": 10,
        "collaboration_mode": "Remote",
        "location": "Skopje"
    },
    {
        "project_id": "P004",
        "title": "SecureNet",
        "description": "Platform for monitoring network security threats",
        "required_skills": "Cybersecurity, Network Security, Python",
        "category": "Cybersecurity",
        "required_role": "Cybersecurity / DevOps",
        "required_experience": "Advanced",
        "hours_per_week": 12,
        "collaboration_mode": "Hybrid",
        "location": "Tetovo"
    },
    {
        "project_id": "P005",
        "title": "DataVision",
        "description": "Business analytics dashboard for visualizing sales data",
        "required_skills": "Python, Pandas, SQL",
        "category": "Data Science",
        "required_role": "Data Scientist",
        "required_experience": "Intermediate",
        "hours_per_week": 8,
        "collaboration_mode": "Remote",
        "location": "Bitola"
    },
    {
        "project_id": "P006",
        "title": "TravelMate",
        "description": "Mobile application for planning trips and travel activities",
        "required_skills": "Flutter, Dart, Firebase",
        "category": "Travel",
        "required_role": "Mobile Developer",
        "required_experience": "Beginner",
        "hours_per_week": 8,
        "collaboration_mode": "Remote",
        "location": "Ohrid"
    },
    {
        "project_id": "P007",
        "title": "HealthAI",
        "description": "AI application for analyzing health and fitness information",
        "required_skills": "Python, Machine Learning, TensorFlow",
        "category": "Health Tech",
        "required_role": "AI Developer",
        "required_experience": "Advanced",
        "hours_per_week": 15,
        "collaboration_mode": "Hybrid",
        "location": "Skopje"
    },
    {
        "project_id": "P008",
        "title": "DesignHub",
        "description": "Collaborative platform for creating and sharing UI designs",
        "required_skills": "Figma, UI/UX, Prototyping",
        "category": "Design",
        "required_role": "UI/UX Designer",
        "required_experience": "Intermediate",
        "hours_per_week": 10,
        "collaboration_mode": "Remote",
        "location": "Tetovo"
    },
    {
        "project_id": "P009",
        "title": "CloudDeploy",
        "description": "Cloud deployment and automation platform",
        "required_skills": "Docker, Kubernetes, CI/CD",
        "category": "Cloud Computing",
        "required_role": "Cybersecurity / DevOps",
        "required_experience": "Advanced",
        "hours_per_week": 12,
        "collaboration_mode": "Remote",
        "location": "Skopje"
    },
    {
        "project_id": "P010",
        "title": "BookFlow",
        "description": "Backend system for managing online book reservations",
        "required_skills": "Java, Spring Boot, SQL",
        "category": "Web Development",
        "required_role": "Backend Developer",
        "required_experience": "Intermediate",
        "hours_per_week": 10,
        "collaboration_mode": "Hybrid",
        "location": "Gostivar"
    }
]

# Combine original and new projects
new_projects_df = pd.DataFrame(new_projects)
expanded_projects = pd.concat(
    [projects, new_projects_df],
    ignore_index=True
)

print("\n=== Expanded Project Dataset ===")
print("Total projects:", len(expanded_projects))
print("Total columns:", len(expanded_projects.columns))
print(
    "Duplicate project IDs:",
    expanded_projects["project_id"].duplicated().sum()
)

print("\nProject titles:")
print(expanded_projects[["project_id", "title"]].to_string(index=False))


# ==========================================
# VALIDATE AND SAVE PROJECT DATASET
# ==========================================

required_project_columns = [
    "project_id",
    "title",
    "description",
    "required_skills",
    "category",
    "required_role",
    "required_experience",
    "hours_per_week",
    "collaboration_mode",
    "location"
]

missing_columns = [
    col for col in required_project_columns
    if col not in expanded_projects.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

missing_values = expanded_projects[required_project_columns].isna().sum().sum()
duplicate_ids = expanded_projects["project_id"].duplicated().sum()

hours = pd.to_numeric(
    expanded_projects["hours_per_week"],
    errors="coerce"
)

invalid_hours = (hours.isna() | (hours <= 0)).sum()

if missing_values or duplicate_ids or invalid_hours:
    raise ValueError(
        f"Validation failed: missing values={missing_values}, "
        f"duplicate IDs={duplicate_ids}, invalid hours={invalid_hours}"
    )

if len(expanded_projects) != 10:
    raise ValueError("Expected exactly 10 projects.")

expanded_projects.to_csv(projects_output_file, index=False)

print("\n=== Projects Dataset Saved Successfully ===")
print("File:", projects_output_file)
print("Projects:", len(expanded_projects))
print("Columns:", len(expanded_projects.columns))
print("Missing values:", missing_values)
print("Duplicate IDs:", duplicate_ids)
print("Invalid hours:", invalid_hours)
