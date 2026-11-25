import pandas as pd
import random
import shutil
from pathlib import Path


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPERIMENTS_DIR = BASE_DIR / "experiments"
BACKUP_DIR = DATA_DIR / "version_1"

USERS_FILE = DATA_DIR / "user_profiles.csv"
PROJECTS_FILE = DATA_DIR / "projects.csv"

TARGET_USERS = 200
TARGET_PROJECTS = 30

# Fixed seed for reproducible dataset generation
random.seed(42)

print("=== CoFound Dataset Expansion V2 ===")


# ==========================================
# 2. PRESERVE THE PREVIOUS DATASET
# ==========================================

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

backup_files = [
    USERS_FILE,
    PROJECTS_FILE,
    DATA_DIR / "evaluation_labels.csv",
    DATA_DIR / "comparison_results.csv",
    EXPERIMENTS_DIR / "experiment_summary.csv",
    EXPERIMENTS_DIR / "error_analysis.csv",
    EXPERIMENTS_DIR / "week9_experiment.md"
]

for source in backup_files:

    destination = BACKUP_DIR / source.name

    if source.exists() and not destination.exists():
        shutil.copy2(source, destination)
        print("Backup created:", destination.name)


# Always use the preserved V1 dataset.
# This prevents duplicate expansion when running again.

users = pd.read_csv(BACKUP_DIR / "user_profiles.csv")
projects = pd.read_csv(BACKUP_DIR / "projects.csv")

if len(users) != 40 or len(projects) != 10:
    raise ValueError(
        "Expected the previous dataset of 40 users and 10 projects."
    )

print("\n=== Previous Dataset ===")
print("Users:", len(users))
print("Projects:", len(projects))


# ==========================================
# 3. DEFINE PROFESSIONAL ROLES AND SKILLS
# ==========================================

role_skills = {

    "AI Developer": [
        ["Python", "Machine Learning", "TensorFlow"],
        ["Python", "NLP", "Scikit-learn"],
        ["Python", "Deep Learning", "PyTorch"],
        ["Python", "Computer Vision", "OpenCV"],
        ["Python", "Machine Learning", "Flask"],
        ["Python", "NLP", "PyTorch"]
    ],

    "Frontend Developer": [
        ["HTML", "CSS", "JavaScript"],
        ["JavaScript", "React", "CSS"],
        ["TypeScript", "React", "Tailwind CSS"],
        ["JavaScript", "Vue", "HTML"],
        ["React", "Next.js", "TypeScript"],
        ["HTML", "CSS", "Bootstrap"]
    ],

    "Backend Developer": [
        ["Python", "Django", "PostgreSQL"],
        ["Java", "Spring Boot", "SQL"],
        ["Node.js", "Express", "MongoDB"],
        ["Python", "FastAPI", "SQL"],
        ["C#", "ASP.NET", "SQL Server"],
        ["Python", "Flask", "PostgreSQL"]
    ],

    "Mobile Developer": [
        ["Kotlin", "Android", "Firebase"],
        ["Swift", "iOS", "SwiftUI"],
        ["Flutter", "Dart", "Firebase"],
        ["React Native", "JavaScript", "Firebase"],
        ["Kotlin", "Java", "Android"],
        ["React Native", "TypeScript", "Firebase"]
    ],

    "UI/UX Designer": [
        ["Figma", "UI/UX", "Prototyping"],
        ["Figma", "Wireframing", "User Research"],
        ["Adobe XD", "UI Design", "Prototyping"],
        ["Figma", "Design Systems", "UX Research"],
        ["UI/UX", "Figma", "Usability Testing"],
        ["Figma", "UI Design", "Wireframing"]
    ],

    "Data Scientist": [
        ["Python", "Pandas", "SQL"],
        ["Python", "Data Analysis", "Scikit-learn"],
        ["R", "Statistics", "Data Visualization"],
        ["Python", "SQL", "Power BI"],
        ["Python", "Pandas", "Tableau"],
        ["Python", "Pandas", "Statistics"]
    ],

    "Cybersecurity / DevOps": [
        ["Linux", "Docker", "AWS"],
        ["Cybersecurity", "Network Security", "Python"],
        ["Docker", "Kubernetes", "CI/CD"],
        ["AWS", "Terraform", "Linux"],
        ["Network Security", "Linux", "Penetration Testing"],
        ["Docker", "Linux", "CI/CD"]
    ]
}


# ==========================================
# 4. ADDITIONAL ROLE-RELATED SKILLS
# ==========================================

additional_skills = {

    "AI Developer": [
        "Pandas", "NumPy", "SQL", "FastAPI",
        "Data Analysis", "Git"
    ],

    "Frontend Developer": [
        "Figma", "Git", "REST API",
        "Bootstrap", "Tailwind CSS", "HTML"
    ],

    "Backend Developer": [
        "Docker", "Git", "REST API",
        "Redis", "SQL", "Linux"
    ],

    "Mobile Developer": [
        "UI/UX", "Git", "REST API",
        "SQLite", "Figma", "Firebase"
    ],

    "UI/UX Designer": [
        "Accessibility", "Graphic Design",
        "HTML", "CSS", "User Research",
        "Usability Testing"
    ],

    "Data Scientist": [
        "NumPy", "Machine Learning", "SQL",
        "Excel", "Data Visualization", "Statistics"
    ],

    "Cybersecurity / DevOps": [
        "Python", "Git", "Linux",
        "AWS", "Bash", "Network Security"
    ]
}


# ==========================================
# 5. DEFINE INTERESTS AND PREFERENCES
# ==========================================

role_interests = {

    "AI Developer": [
        "AI", "Education", "Education & AI",
        "Health Tech", "Automation",
        "Machine Learning", "Technology"
    ],

    "Frontend Developer": [
        "Web Development", "Design",
        "E-commerce", "Business", "Education"
    ],

    "Backend Developer": [
        "Web Development", "Databases",
        "Business", "Backend", "E-commerce"
    ],

    "Mobile Developer": [
        "Mobile Apps", "Health & Fitness",
        "Travel", "Health Tech",
        "Education", "Technology"
    ],

    "UI/UX Designer": [
        "Design", "Mobile Apps",
        "User Experience", "Web Development",
        "E-commerce"
    ],

    "Data Scientist": [
        "Data Science", "Business",
        "Analytics", "AI",
        "Finance", "Health Tech"
    ],

    "Cybersecurity / DevOps": [
        "Cybersecurity", "Cloud Computing",
        "Security", "Technology", "Automation"
    ]
}

roles = list(role_skills.keys())

experience_levels = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

collaboration_modes = [
    "Remote",
    "Hybrid",
    "On-site"
]

locations = [
    "Tetovo",
    "Skopje",
    "Bitola",
    "Ohrid",
    "Gostivar",
    "Kumanovo",
    "Prilep",
    "Struga"
]


# ==========================================
# 6. GENERATE 160 NEW USER PROFILES
# ==========================================

new_profiles = []

number_of_new_users = TARGET_USERS - len(users)

for i in range(number_of_new_users):

    user_number = len(users) + i + 1

    # Distribute users across all professional roles
    role = roles[i % len(roles)]

    # Generate different experience levels
    experience = random.choices(
        experience_levels,
        weights=[35, 45, 20],
        k=1
    )[0]

    # Select a realistic role-based skill combination
    skills = random.choice(role_skills[role]).copy()

    # Vary the number of skills according to experience
    if experience == "Beginner":
        target_skill_count = random.randint(2, 3)

    elif experience == "Intermediate":
        target_skill_count = random.randint(3, 5)

    else:
        target_skill_count = random.randint(4, 7)

    # Add or remove skills to create different profiles
    if target_skill_count < len(skills):

        skills = random.sample(
            skills,
            target_skill_count
        )

    else:

        available_extra_skills = [
            skill
            for skill in additional_skills[role]
            if skill not in skills
        ]

        extra_count = min(
            target_skill_count - len(skills),
            len(available_extra_skills)
        )

        skills.extend(
            random.sample(
                available_extra_skills,
                extra_count
            )
        )

    # Generate different interests
    interests = random.sample(
        role_interests[role],
        random.randint(1, 3)
    )

    # Generate preferred project categories
    preferred_types = random.sample(
        role_interests[role],
        random.randint(1, 3)
    )

    # Generate varied weekly availability
    availability = random.choice([
        3, 5, 6, 8, 10, 12,
        15, 18, 20, 25, 30
    ])

    # Generate collaboration preferences
    collaboration_mode = random.choices(
        collaboration_modes,
        weights=[50, 35, 15],
        k=1
    )[0]

    new_profiles.append({

        "user_id": f"U{user_number:03d}",

        "name": f"Synthetic User {user_number:03d}",

        "skills": ", ".join(skills),

        "interests": ", ".join(interests),

        "experience": experience,

        "availability": availability,

        "preferred_role": role,

        "preferred_project_types": ", ".join(
            preferred_types
        ),

        "collaboration_mode": collaboration_mode,

        "location": random.choice(locations)

    })


# Combine previous and new profiles
new_users = pd.DataFrame(new_profiles)

expanded_users = pd.concat(
    [users, new_users],
    ignore_index=True
)


# ==========================================
# 7. DEFINE 20 ADDITIONAL PROJECTS
# ==========================================

# Each project has a specific description,
# required skills, role and category.

project_templates = [

    (
        "EcoTrack",
        "Application for tracking personal carbon emissions",
        "Python, Pandas, SQL",
        "Data Science",
        "Data Scientist"
    ),

    (
        "StudyBuddy",
        "AI assistant for organizing learning materials",
        "Python, NLP, Scikit-learn",
        "Education & AI",
        "AI Developer"
    ),

    (
        "MarketPlace",
        "Online marketplace for local businesses",
        "React, JavaScript, CSS",
        "E-commerce",
        "Frontend Developer"
    ),

    (
        "TaskFlow",
        "Backend service for managing team tasks",
        "Python, FastAPI, SQL",
        "Web Development",
        "Backend Developer"
    ),

    (
        "FoodFinder",
        "Mobile application for discovering restaurants",
        "Flutter, Dart, Firebase",
        "Mobile Apps",
        "Mobile Developer"
    ),

    (
        "CreativeSpace",
        "Collaborative design platform for creative teams",
        "Figma, UI/UX, Prototyping",
        "Design",
        "UI/UX Designer"
    ),

    (
        "FinanceLens",
        "Financial analytics and reporting dashboard",
        "Python, SQL, Power BI",
        "Finance",
        "Data Scientist"
    ),

    (
        "ThreatGuard",
        "System for detecting network security risks",
        "Cybersecurity, Network Security, Python",
        "Cybersecurity",
        "Cybersecurity / DevOps"
    ),

    (
        "CloudSync",
        "Automated cloud infrastructure management system",
        "AWS, Terraform, Linux",
        "Cloud Computing",
        "Cybersecurity / DevOps"
    ),

    (
        "VisionAI",
        "Image recognition application using computer vision",
        "Python, Computer Vision, OpenCV",
        "AI",
        "AI Developer"
    ),

    (
        "EventConnect",
        "Responsive website for discovering local events",
        "React, Next.js, TypeScript",
        "Web Development",
        "Frontend Developer"
    ),

    (
        "MedRecord",
        "Backend system for managing healthcare records",
        "Java, Spring Boot, SQL",
        "Health Tech",
        "Backend Developer"
    ),

    (
        "HabitHero",
        "Mobile application for tracking daily habits",
        "Kotlin, Android, Firebase",
        "Health & Fitness",
        "Mobile Developer"
    ),

    (
        "AccessibleWeb",
        "Accessible interface design for online services",
        "Figma, UI/UX, Accessibility",
        "Design",
        "UI/UX Designer"
    ),

    (
        "SalesInsight",
        "Application for analyzing customer sales trends",
        "Python, Pandas, Tableau",
        "Business",
        "Data Scientist"
    ),

    (
        "ChatAssist",
        "Intelligent chatbot for answering customer questions",
        "Python, NLP, PyTorch",
        "AI",
        "AI Developer"
    ),

    (
        "DevPipeline",
        "Automated software testing and deployment pipeline",
        "Docker, Kubernetes, CI/CD",
        "Cloud Computing",
        "Cybersecurity / DevOps"
    ),

    (
        "PortfolioHub",
        "Website for showcasing professional portfolios",
        "HTML, CSS, JavaScript",
        "Web Development",
        "Frontend Developer"
    ),

    (
        "QuickReserve",
        "Backend platform for managing online reservations",
        "Node.js, Express, MongoDB",
        "Business",
        "Backend Developer"
    ),

    (
        "CityExplorer",
        "Mobile travel guide for discovering city attractions",
        "React Native, JavaScript, Firebase",
        "Travel",
        "Mobile Developer"
    )
]


# ==========================================
# 8. GENERATE PROJECT REQUIREMENTS
# ==========================================

new_projects = []

for i, template in enumerate(project_templates):

    (
        title,
        description,
        required_skills,
        category,
        required_role
    ) = template

    project_number = len(projects) + i + 1

    required_experience = random.choices(
        experience_levels,
        weights=[25, 50, 25],
        k=1
    )[0]

    hours_per_week = random.choice([
        5, 8, 10, 12, 15, 20
    ])

    collaboration_mode = random.choices(
        collaboration_modes,
        weights=[50, 35, 15],
        k=1
    )[0]

    new_projects.append({

        "project_id": f"P{project_number:03d}",

        "title": title,

        "description": description,

        "required_skills": required_skills,

        "category": category,

        "required_role": required_role,

        "required_experience": required_experience,

        "hours_per_week": hours_per_week,

        "collaboration_mode": collaboration_mode,

        "location": random.choice(locations)

    })


# Combine previous and new projects
new_projects_df = pd.DataFrame(new_projects)

expanded_projects = pd.concat(
    [projects, new_projects_df],
    ignore_index=True
)


# ==========================================
# 9. VALIDATE USER DATASET
# ==========================================

required_user_columns = [

    "user_id",
    "name",
    "skills",
    "interests",
    "experience",
    "availability",
    "preferred_role",
    "preferred_project_types",
    "collaboration_mode",
    "location"

]

missing_user_columns = [
    column
    for column in required_user_columns
    if column not in expanded_users.columns
]

if missing_user_columns:
    raise ValueError(
        f"Missing user columns: {missing_user_columns}"
    )

user_missing_values = (
    expanded_users[required_user_columns]
    .isna()
    .sum()
    .sum()
)

duplicate_user_ids = (
    expanded_users["user_id"]
    .duplicated()
    .sum()
)

user_hours = pd.to_numeric(
    expanded_users["availability"],
    errors="coerce"
)

invalid_user_hours = (
    user_hours.isna() |
    (user_hours < 0) |
    (user_hours > 168)
).sum()

invalid_user_experience = (
    ~expanded_users["experience"].isin(experience_levels)
).sum()

invalid_user_roles = (
    ~expanded_users["preferred_role"].isin(roles)
).sum()

invalid_user_modes = (
    ~expanded_users["collaboration_mode"].isin(
        collaboration_modes
    )
).sum()

if (
    user_missing_values
    or duplicate_user_ids
    or invalid_user_hours
    or invalid_user_experience
    or invalid_user_roles
    or invalid_user_modes
):

    raise ValueError("User dataset validation failed.")

if len(expanded_users) != TARGET_USERS:

    raise ValueError(
        f"Expected exactly {TARGET_USERS} users."
    )


# ==========================================
# 10. VALIDATE PROJECT DATASET
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

missing_project_columns = [
    column
    for column in required_project_columns
    if column not in expanded_projects.columns
]

if missing_project_columns:

    raise ValueError(
        f"Missing project columns: {missing_project_columns}"
    )

project_missing_values = (
    expanded_projects[required_project_columns]
    .isna()
    .sum()
    .sum()
)

duplicate_project_ids = (
    expanded_projects["project_id"]
    .duplicated()
    .sum()
)

project_hours = pd.to_numeric(
    expanded_projects["hours_per_week"],
    errors="coerce"
)

invalid_project_hours = (
    project_hours.isna() |
    (project_hours <= 0) |
    (project_hours > 168)
).sum()

invalid_project_experience = (
    ~expanded_projects["required_experience"].isin(
        experience_levels
    )
).sum()

invalid_project_roles = (
    ~expanded_projects["required_role"].isin(roles)
).sum()

invalid_project_modes = (
    ~expanded_projects["collaboration_mode"].isin(
        collaboration_modes
    )
).sum()

if (
    project_missing_values
    or duplicate_project_ids
    or invalid_project_hours
    or invalid_project_experience
    or invalid_project_roles
    or invalid_project_modes
):

    raise ValueError("Project dataset validation failed.")

if len(expanded_projects) != TARGET_PROJECTS:

    raise ValueError(
        f"Expected exactly {TARGET_PROJECTS} projects."
    )


# ==========================================
# 11. SAVE THE IMPROVED DATASETS
# ==========================================

expanded_users.to_csv(
    USERS_FILE,
    index=False
)

expanded_projects.to_csv(
    PROJECTS_FILE,
    index=False
)


# ==========================================
# 12. DISPLAY DATASET SUMMARY
# ==========================================

print("\n=== Expanded Dataset Summary ===")

print("Previous users:", len(users))
print("New users:", len(new_users))
print("Total users:", len(expanded_users))

print("\nPrevious projects:", len(projects))
print("New projects:", len(new_projects_df))
print("Total projects:", len(expanded_projects))

print(
    "\nTotal project-user combinations:",
    len(expanded_users) * len(expanded_projects)
)

print("\n=== User Role Distribution ===")

print(
    expanded_users["preferred_role"]
    .value_counts()
    .to_string()
)

print("\n=== Experience Distribution ===")

print(
    expanded_users["experience"]
    .value_counts()
    .to_string()
)

print("\n=== Collaboration Mode Distribution ===")

print(
    expanded_users["collaboration_mode"]
    .value_counts()
    .to_string()
)

print("\n=== Availability Statistics ===")

print(
    expanded_users["availability"]
    .describe()
    .round(2)
    .to_string()
)

print("\n=== Project Category Distribution ===")

print(
    expanded_projects["category"]
    .value_counts()
    .to_string()
)

print("\n=== Dataset Validation ===")

print("Missing user values:", user_missing_values)
print("Duplicate user IDs:", duplicate_user_ids)
print("Invalid user availability:", invalid_user_hours)
print("Invalid user experience:", invalid_user_experience)
print("Invalid user roles:", invalid_user_roles)
print("Invalid user modes:", invalid_user_modes)

print("Missing project values:", project_missing_values)
print("Duplicate project IDs:", duplicate_project_ids)
print("Invalid project hours:", invalid_project_hours)
print("Invalid project experience:", invalid_project_experience)
print("Invalid project roles:", invalid_project_roles)
print("Invalid project modes:", invalid_project_modes)

print("\n=== Dataset Saved Successfully ===")

print("Users file:", USERS_FILE)
print("Projects file:", PROJECTS_FILE)
print("Previous dataset backup:", BACKUP_DIR)

print("\nCoFound Dataset Expansion V2 completed!")