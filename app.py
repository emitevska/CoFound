import streamlit as st
import pandas as pd
import math

from pathlib import Path
from html import escape

import matching


# ==========================================
# 1. APPLICATION CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CoFound | Connect. Collaborate. Create.",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

USERS_FILE = DATA_DIR / "user_profiles.csv"
PROJECTS_FILE = DATA_DIR / "projects.csv"

CSS_FILE = ASSETS_DIR / "styles.css"
LOGO_FILE = ASSETS_DIR / "logo.svg"


# ==========================================
# 2. LOAD EXTERNAL STYLESHEET
# ==========================================

def load_css():

    with open(CSS_FILE, encoding="utf-8") as file:

        st.html(
            f"<style>{file.read()}</style>"
        )


load_css()


# ==========================================
# 3. LOAD AND REFRESH DATA
# ==========================================

users = pd.read_csv(USERS_FILE)
projects = pd.read_csv(PROJECTS_FILE)

matching.users = users.copy()
matching.projects = projects.copy()


# ==========================================
# 4. AVAILABLE OPTIONS
# ==========================================

ROLES = [
    "AI Developer",
    "Frontend Developer",
    "Backend Developer",
    "Mobile Developer",
    "UI/UX Designer",
    "Data Scientist",
    "Cybersecurity / DevOps"
]

# Internal values remain unchanged so that
# the existing AI algorithm works correctly.

EXPERIENCE_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

# Experience labels displayed in the interface.

EXPERIENCE_LABELS = {
    "Beginner": "0–1 years",
    "Intermediate": "2–4 years",
    "Advanced": "5+ years",
    "All levels": "All experience ranges"
}

# Minimum years represented by each category.

MINIMUM_EXPERIENCE = {
    "Beginner": "0 years",
    "Intermediate": "2 years",
    "Advanced": "5 years"
}


def experience_label(value):

    return EXPERIENCE_LABELS.get(value, value)


def minimum_experience_label(value):

    return MINIMUM_EXPERIENCE.get(value, value)


COLLABORATION_MODES = [
    "Remote",
    "Hybrid",
    "On-site"
]

CATEGORIES = [
    "AI",
    "Education",
    "Education & AI",
    "Web Development",
    "Mobile Apps",
    "Design",
    "Data Science",
    "Cybersecurity",
    "Cloud Computing",
    "Health & Fitness",
    "Health Tech",
    "Travel",
    "Business",
    "E-commerce",
    "Finance",
    "Technology",
    "Automation",
    "Databases",
    "Other"
]

LOCATIONS = [
    "Tetovo",
    "Skopje",
    "Bitola",
    "Ohrid",
    "Gostivar",
    "Kumanovo",
    "Prilep",
    "Struga",
    "Other"
]

PROJECT_ICONS = {
    "AI": "✦",
    "Education & AI": "✦",
    "Education": "▤",
    "Web Development": "⌘",
    "Mobile Apps": "▣",
    "Design": "◇",
    "Data Science": "▥",
    "Cybersecurity": "⬡",
    "Cloud Computing": "☁",
    "Health & Fitness": "♡",
    "Health Tech": "♡",
    "Travel": "◎",
    "Business": "▦",
    "E-commerce": "▣",
    "Finance": "↗"
}


# Collect available skills.

available_skills = set()

for value in users["skills"].dropna():

    available_skills.update(
        skill.strip()
        for skill in str(value).split(",")
        if skill.strip()
    )

for value in projects["required_skills"].dropna():

    available_skills.update(
        skill.strip()
        for skill in str(value).split(",")
        if skill.strip()
    )

SKILLS = sorted(
    available_skills,
    key=str.lower
)


# ==========================================
# 5. SESSION STATE
# ==========================================

if "page" not in st.session_state:
    st.session_state.page = "Overview"

if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

if "recommendation_project" not in st.session_state:
    st.session_state.recommendation_project = None


def navigate(page):

    st.session_state.page = page


def open_matching(project_id):

    st.session_state.selected_project = project_id
    st.session_state.recommendation_project = None
    st.session_state.page = "AI Matching"

    st.session_state.pop(
        "matching_selector",
        None
    )


# ==========================================
# 6. GENERAL HELPER FUNCTIONS
# ==========================================

def safe(value):

    if pd.isna(value):
        return ""

    return escape(str(value))


def get_initials(name):

    words = str(name).strip().split()

    if not words:
        return "?"

    return "".join(
        word[0].upper()
        for word in words[:2]
    )


def generate_id(dataframe, column, prefix):

    numbers = []

    for value in dataframe[column]:

        value = str(value)

        if value.startswith(prefix):

            number = value[len(prefix):]

            if number.isdigit():
                numbers.append(int(number))

    return f"{prefix}{max(numbers, default=0) + 1:03d}"


def combine_skills(selected, custom):

    result = {}

    for skill in selected:

        skill = skill.strip()

        if skill:
            result[skill.lower()] = skill

    for skill in custom.split(","):

        skill = skill.strip()

        if skill:
            result[skill.lower()] = skill

    return ", ".join(result.values())


def save_user(profile):

    current_users = pd.read_csv(USERS_FILE)

    profile["user_id"] = generate_id(
        current_users,
        "user_id",
        "U"
    )

    updated_users = pd.concat(
        [
            current_users,
            pd.DataFrame([profile])
        ],
        ignore_index=True
    )

    updated_users.to_csv(
        USERS_FILE,
        index=False
    )


def save_project(project):

    current_projects = pd.read_csv(PROJECTS_FILE)

    project["project_id"] = generate_id(
        current_projects,
        "project_id",
        "P"
    )

    updated_projects = pd.concat(
        [
            current_projects,
            pd.DataFrame([project])
        ],
        ignore_index=True
    )

    updated_projects.to_csv(
        PROJECTS_FILE,
        index=False
    )


# ==========================================
# 7. REUSABLE DESIGN COMPONENTS
# ==========================================

def render_html(content):

    st.html(content)


def page_header(section, title, description):

    render_html(f"""
    <div class="page-eyebrow">
        WORKSPACE / {safe(section)}
    </div>

    <h1>{safe(title)}</h1>

    <div class="page-description">
        {safe(description)}
    </div>
    """)


def skill_tags(skills, style=""):

    if pd.isna(skills):
        return ""

    items = [
        item.strip()
        for item in str(skills).split(",")
        if item.strip()
    ]

    tags = "".join(
        f'<span class="skill-tag {style}">'
        f'{safe(item)}</span>'
        for item in items
    )

    return f'<div class="skill-list">{tags}</div>'


def stat_card(icon, value, label):

    render_html(f"""
    <div class="stat-card">

        <div class="stat-icon">
            {icon}
        </div>

        <div class="stat-value">
            {safe(value)}
        </div>

        <div class="stat-label">
            {safe(label)}
        </div>

    </div>
    """)


def project_card(project):

    icon = PROJECT_ICONS.get(
        project["category"],
        "◇"
    )

    experience = minimum_experience_label(
        project["required_experience"]
    )

    render_html(f"""
    <div class="project-card">

        <div class="project-header">

            <div class="project-icon">
                {icon}
            </div>

            <div>

                <div class="project-title">
                    {safe(project["title"])}
                </div>

                <div class="project-category">
                    {safe(project["category"])}
                    · {safe(project["project_id"])}
                </div>

            </div>

        </div>

        <div class="project-description">
            {safe(project["description"])}
        </div>

        {skill_tags(project["required_skills"])}

        <div class="project-meta">

            <b>Role:</b>
            {safe(project["required_role"])}<br>

            <b>Minimum experience:</b>
            {safe(experience)}<br>

            <b>Commitment:</b>
            {safe(project["hours_per_week"])} hours/week<br>

            <b>Collaboration:</b>
            {safe(project["collaboration_mode"])}<br>

            <b>Location:</b>
            {safe(project["location"])}

        </div>

    </div>
    """)


def profile_card(user):

    initials = get_initials(user["name"])

    experience = experience_label(
        user["experience"]
    )

    render_html(f"""
    <div class="profile-card">

        <div class="profile-header">

            <div class="avatar">
                {safe(initials)}
            </div>

            <div>

                <div class="profile-name">
                    {safe(user["name"])}
                </div>

                <div class="profile-role">
                    {safe(user["preferred_role"])}
                </div>

            </div>

        </div>

        {skill_tags(user["skills"])}

        <div class="profile-meta">

            <b>Experience:</b>
            {safe(experience)}<br>

            <b>Availability:</b>
            {safe(user["availability"])} hours/week<br>

            <b>Collaboration:</b>
            {safe(user["collaboration_mode"])}<br>

            <b>Location:</b>
            {safe(user["location"])}

        </div>

    </div>
    """)


def empty_state(title, description):

    render_html(f"""
    <div class="empty-state">

        <div class="empty-icon">
            ◎
        </div>

        <div class="empty-title">
            {safe(title)}
        </div>

        <div class="empty-description">
            {safe(description)}
        </div>

    </div>
    """)


def recommendation_card(
    candidate,
    rank,
    required_skills
):

    score = max(
        0.0,
        min(100.0, float(candidate["match_score"]))
    )

    experience = experience_label(
        candidate["experience"]
    )

    candidate_skills = matching.split_items(
        candidate["skills"]
    )

    matched_skills = sorted(
        candidate_skills & required_skills
    )

    missing_skills = sorted(
        required_skills - candidate_skills
    )

    matched_html = skill_tags(
        ", ".join(matched_skills),
        "matched"
    )

    if missing_skills:

        missing_html = skill_tags(
            ", ".join(missing_skills),
            "missing"
        )

    else:

        missing_html = """
        <div class="profile-meta">
            No missing required skills
        </div>
        """

    render_html(f"""
    <div class="recommendation-card">

        <div class="recommendation-header">

            <span class="rank-label">
                #{rank} RECOMMENDATION
            </span>

            <div class="score-ring"
                 style="--score: {score};">

                <div class="score-inner">

                    <div class="score-number">
                        {score:.1f}
                    </div>

                    <div class="score-caption">
                        MATCH / 100
                    </div>

                </div>

            </div>

        </div>

        <div class="profile-header">

            <div class="avatar">
                {safe(get_initials(candidate["name"]))}
            </div>

            <div>

                <div class="profile-name">
                    {safe(candidate["name"])}
                </div>

                <div class="profile-role">
                    {safe(candidate["preferred_role"])}
                </div>

            </div>

        </div>

        <div class="profile-meta">

            <b>Experience:</b>
            {safe(experience)}<br>

            <b>Availability:</b>
            {safe(candidate["availability"])} hours/week<br>

            <b>Collaboration:</b>
            {safe(candidate["collaboration_mode"])}<br>

            <b>Location:</b>
            {safe(candidate["location"])}

        </div>

        <div class="profile-meta"
             style="margin-top: 15px;">

            <b>Matching skills</b>

        </div>

        {matched_html}

        <div class="profile-meta">
            <b>Missing project skills</b>
        </div>

        {missing_html}

        <div class="eligible-label">
            ✓ Meets mandatory requirements
        </div>

    </div>
    """)


# ==========================================
# 8. SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:

    st.image(
        str(LOGO_FILE),
        width="stretch"
    )

    render_html("""
    <div class="sidebar-section">
        WORKSPACE
    </div>
    """)

    navigation_items = [
        ("Overview", ":material/dashboard:"),
        ("Community", ":material/group:"),
        ("Projects", ":material/folder_open:"),
        ("AI Matching", ":material/auto_awesome:"),
        ("About CoFound", ":material/info:")
    ]

    for page_name, icon in navigation_items:

        active = st.session_state.page == page_name

        st.button(
            page_name,
            icon=icon,
            key=f"nav_{page_name}",
            type="primary" if active else "secondary",
            width="stretch",
            on_click=navigate,
            args=(page_name,)
        )

 

page = st.session_state.page

if "success_message" in st.session_state:

    st.success(
        st.session_state.pop("success_message")
    )


# ==========================================
# 9. OVERVIEW PAGE
# ==========================================

if page == "Overview":

    render_html("""
    <div class="page-eyebrow">
        WORKSPACE / OVERVIEW
    </div>

    <div class="hero">

        <div class="eyebrow">
            CONNECT. COLLABORATE. CREATE.
        </div>

        <h1>
            Great projects start with
            <span class="hero-highlight">
                great people.
            </span>
        </h1>

        <p>
            Find collaborators who share your interests,
            complement your skills and bring your ideas
            to life. Powered by intelligent AI matching.
        </p>

    </div>
    """)

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:

        st.button(
            "Find collaborators",
            icon=":material/auto_awesome:",
            type="primary",
            width="stretch",
            on_click=navigate,
            args=("AI Matching",)
        )

    with col2:

        st.button(
            "Explore projects",
            icon=":material/arrow_forward:",
            width="stretch",
            on_click=navigate,
            args=("Projects",)
        )

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        stat_card(
            "♙",
            len(users),
            "Collaborator profiles"
        )

    with col2:

        stat_card(
            "▦",
            len(projects),
            "Available projects"
        )

    with col3:

        stat_card(
            "◇",
            users["preferred_role"].nunique(),
            "Professional roles"
        )

    with col4:

        stat_card(
            "✦",
            f"{len(users) * len(projects):,}",
            "Possible combinations"
        )

    st.divider()

    left, right = st.columns([4, 1])

    with left:

        st.header("Featured projects")

        st.caption(
            "Explore opportunities and discover "
            "your next collaboration."
        )

    with right:

        st.button(
            "View all projects",
            width="stretch",
            on_click=navigate,
            args=("Projects",)
        )

    columns = st.columns(3)

    for i, (_, project) in enumerate(
        projects.head(3).iterrows()
    ):

        with columns[i]:

            project_card(project)

            st.button(
                "Find collaborators",
                key=f"featured_{project['project_id']}",
                width="stretch",
                on_click=open_matching,
                args=(project["project_id"],)
            )

    st.divider()

    st.header("How CoFound works")

    columns = st.columns(3)

    steps = [
        (
            "01",
            "Create your profile",
            "Add your skills, experience, interests "
            "and collaboration preferences."
        ),
        (
            "02",
            "Post a project",
            "Describe your idea and define the "
            "requirements for your ideal collaborator."
        ),
        (
            "03",
            "Discover your matches",
            "Our AI ranks suitable candidates "
            "and explains their compatibility."
        )
    ]

    for i, (number, title, description) in enumerate(steps):

        with columns[i]:

            render_html(f"""
            <div class="content-card">

                <div class="stat-icon">
                    {number}
                </div>

                <div class="section-title">
                    {title}
                </div>

                <div class="section-description">
                    {description}
                </div>

            </div>
            """)

    st.divider()

    st.header("Community insights")

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.subheader("Professional roles")

            st.bar_chart(
                users["preferred_role"].value_counts(),
                color="#6D4AFF",
                horizontal=True
            )

    with col2:

        with st.container(border=True):

            st.subheader("Years of experience")

            experience_counts = (
                users["experience"]
                .map(experience_label)
                .value_counts()
                .reindex(
                    [
                        "0–1 years",
                        "2–4 years",
                        "5+ years"
                    ],
                    fill_value=0
                )
            )

            st.bar_chart(
                experience_counts,
                color="#A78BFA"
            )

    st.caption(
        "The initial CoFound community consists of "
        "synthetic demonstration profiles."
    )


# ==========================================
# 10. COMMUNITY PAGE
# ==========================================

elif page == "Community":

    page_header(
        "Community",
        "Discover talented collaborators",
        "Explore the community and find "
        "people who complement your skills."
    )

    browse_tab, create_tab = st.tabs([
        "Browse community",
        "Create profile"
    ])

    # --------------------------------------
    # BROWSE PROFILES
    # --------------------------------------

    with browse_tab:

        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:

            search = st.text_input(
                "Search collaborators",
                placeholder="Search by name or skill..."
            )

        with col2:

            selected_role = st.selectbox(
                "Professional role",
                ["All roles"] + ROLES
            )

        with col3:

            selected_experience = st.selectbox(
                "Years of experience",
                ["All levels"] + EXPERIENCE_LEVELS,
                format_func=experience_label
            )

        filtered_users = users.copy()

        if search.strip():

            filtered_users = filtered_users[
                filtered_users["name"].str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
                |
                filtered_users["skills"].str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        if selected_role != "All roles":

            filtered_users = filtered_users[
                filtered_users["preferred_role"]
                == selected_role
            ]

        if selected_experience != "All levels":

            filtered_users = filtered_users[
                filtered_users["experience"]
                == selected_experience
            ]

        st.caption(
            f"{len(filtered_users)} collaborators found"
        )

        if filtered_users.empty:

            empty_state(
                "No collaborators found",
                "Try another search or change your filters."
            )

        else:

            profiles_per_page = 12

            total_pages = max(
                1,
                math.ceil(
                    len(filtered_users) / profiles_per_page
                )
            )

            current_page = st.selectbox(
                "Page",
                list(range(1, total_pages + 1)),
                format_func=lambda number: (
                    f"Page {number} of {total_pages}"
                ),
                key=(
                    f"community_page_{search}_"
                    f"{selected_role}_{selected_experience}"
                )
            )

            start = (
                current_page - 1
            ) * profiles_per_page

            end = start + profiles_per_page

            visible_users = filtered_users.iloc[
                start:end
            ]

            columns = st.columns(3)

            for i, (_, user) in enumerate(
                visible_users.iterrows()
            ):

                with columns[i % 3]:

                    profile_card(user)

                    st.write("")

    # --------------------------------------
    # CREATE PROFILE
    # --------------------------------------

    with create_tab:

        st.subheader("Build your collaborator profile")

        st.caption(
            "Your profile information will be used "
            "to recommend you for suitable projects."
        )

        with st.form("create_user_form"):

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### Personal information")

                name = st.text_input(
                    "Display name *",
                    max_chars=80
                )

                role = st.selectbox(
                    "Preferred role *",
                    ROLES
                )

                experience = st.selectbox(
                    "Years of experience *",
                    EXPERIENCE_LEVELS,
                    format_func=experience_label,
                    help=(
                        "Select the range that best "
                        "represents your experience."
                    )
                )

                location = st.selectbox(
                    "Location",
                    LOCATIONS
                )

                availability = st.number_input(
                    "Available hours per week *",
                    min_value=1,
                    max_value=60,
                    value=10
                )

            with col2:

                st.markdown("### Skills and preferences")

                selected_skills = st.multiselect(
                    "Your skills *",
                    SKILLS
                )

                custom_skills = st.text_input(
                    "Additional skills",
                    placeholder="Separate skills with commas",
                    max_chars=300
                )

                interests = st.multiselect(
                    "Your interests *",
                    CATEGORIES
                )

                preferred_types = st.multiselect(
                    "Preferred project categories *",
                    CATEGORIES
                )

                collaboration = st.selectbox(
                    "Collaboration preference",
                    COLLABORATION_MODES
                )

            st.caption(
                "Use demonstration information only. "
                "This prototype does not provide "
                "private user accounts."
            )

            submitted = st.form_submit_button(
                "Create profile",
                type="primary",
                icon=":material/person_add:"
            )

            if submitted:

                skills = combine_skills(
                    selected_skills,
                    custom_skills
                )

                if not name.strip():

                    st.error(
                        "Please enter a display name."
                    )

                elif not skills:

                    st.error(
                        "Please enter at least one skill."
                    )

                elif not interests:

                    st.error(
                        "Please select at least one interest."
                    )

                elif not preferred_types:

                    st.error(
                        "Please select at least one "
                        "preferred project category."
                    )

                else:

                    profile = {
                        "name": name.strip(),
                        "skills": skills,
                        "interests": ", ".join(interests),
                        "experience": experience,
                        "availability": int(availability),
                        "preferred_role": role,
                        "preferred_project_types": ", ".join(
                            preferred_types
                        ),
                        "collaboration_mode": collaboration,
                        "location": location
                    }

                    try:

                        save_user(profile)

                        st.session_state.success_message = (
                            "Your profile was created successfully "
                            "and is now available for AI matching."
                        )

                        st.rerun()

                    except OSError as error:

                        st.error(
                            f"Unable to save profile: {error}"
                        )


# ==========================================
# 11. PROJECTS PAGE
# ==========================================

elif page == "Projects":

    page_header(
        "Projects",
        "Explore new opportunities",
        "Discover exciting projects or share your "
        "own idea with the CoFound community."
    )

    browse_tab, create_tab = st.tabs([
        "Explore projects",
        "Post a project"
    ])

    # --------------------------------------
    # BROWSE PROJECTS
    # --------------------------------------

    with browse_tab:

        col1, col2 = st.columns([2, 1])

        with col1:

            search = st.text_input(
                "Search projects",
                placeholder="Search by title or description..."
            )

        with col2:

            category_filter = st.selectbox(
                "Category",
                ["All categories"] + sorted(
                    projects["category"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        filtered_projects = projects.copy()

        if search.strip():

            filtered_projects = filtered_projects[
                filtered_projects["title"].str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
                |
                filtered_projects["description"].str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        if category_filter != "All categories":

            filtered_projects = filtered_projects[
                filtered_projects["category"]
                == category_filter
            ]

        st.caption(
            f"{len(filtered_projects)} projects found"
        )

        if filtered_projects.empty:

            empty_state(
                "No projects found",
                "Try another search or choose "
                "a different category."
            )

        else:

            columns = st.columns(3)

            for i, (_, project) in enumerate(
                filtered_projects.iterrows()
            ):

                with columns[i % 3]:

                    project_card(project)

                    st.button(
                        "Find collaborators",
                        key=f"project_{project['project_id']}",
                        width="stretch",
                        on_click=open_matching,
                        args=(project["project_id"],)
                    )

                    st.write("")

    # --------------------------------------
    # POST A PROJECT
    # --------------------------------------

    with create_tab:

        st.subheader("Bring your next idea to life")

        st.caption(
            "Define your project requirements "
            "to discover compatible collaborators."
        )

        with st.form("create_project_form"):

            title = st.text_input(
                "Project title *",
                max_chars=100
            )

            description = st.text_area(
                "Project description *",
                placeholder=(
                    "What is your project about? "
                    "What would you like to achieve?"
                ),
                max_chars=1500,
                height=130
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### Project requirements")

                category = st.selectbox(
                    "Project category *",
                    CATEGORIES
                )

                required_role = st.selectbox(
                    "Required professional role *",
                    ROLES
                )

                required_experience = st.selectbox(
                    "Minimum years of experience *",
                    EXPERIENCE_LEVELS,
                    format_func=minimum_experience_label,
                    help=(
                        "Select the minimum experience "
                        "required for your project."
                    )
                )

                required_hours = st.number_input(
                    "Required hours per week *",
                    min_value=1,
                    max_value=60,
                    value=10
                )

            with col2:

                st.markdown("### Skills and collaboration")

                selected_skills = st.multiselect(
                    "Required skills *",
                    SKILLS
                )

                custom_skills = st.text_input(
                    "Additional required skills",
                    placeholder="Separate skills with commas",
                    max_chars=300
                )

                collaboration = st.selectbox(
                    "Collaboration mode",
                    COLLABORATION_MODES
                )

                location = st.selectbox(
                    "Project location",
                    LOCATIONS
                )

            submitted = st.form_submit_button(
                "Publish project",
                type="primary",
                icon=":material/add_circle:"
            )

            if submitted:

                required_skills = combine_skills(
                    selected_skills,
                    custom_skills
                )

                if not title.strip():

                    st.error(
                        "Please enter a project title."
                    )

                elif len(description.strip()) < 10:

                    st.error(
                        "Please provide a description "
                        "of at least 10 characters."
                    )

                elif not required_skills:

                    st.error(
                        "Please enter at least one "
                        "required skill."
                    )

                else:

                    project = {
                        "title": title.strip(),
                        "description": description.strip(),
                        "required_skills": required_skills,
                        "category": category,
                        "required_role": required_role,
                        "required_experience": (
                            required_experience
                        ),
                        "hours_per_week": int(required_hours),
                        "collaboration_mode": collaboration,
                        "location": location
                    }

                    try:

                        save_project(project)

                        st.session_state.success_message = (
                            "Your project was published successfully. "
                            "You can now find AI collaborators."
                        )

                        open_matching(
                            project["project_id"]
                        )

                        st.rerun()

                    except OSError as error:

                        st.error(
                            f"Unable to save project: {error}"
                        )


# ==========================================
# 12. AI MATCHING PAGE
# ==========================================

elif page == "AI Matching":

    page_header(
        "AI Matching",
        "Find your next collaborator",
        "Discover the right people for your project "
        "with intelligent, explainable AI matching."
    )

    if projects.empty:

        empty_state(
            "No projects available",
            "Create a project before searching "
            "for collaborators."
        )

    else:

        project_options = {
            row["project_id"]: (
                f'{row["title"]} — {row["category"]}'
            )
            for _, row in projects.iterrows()
        }

        project_ids = list(project_options.keys())

        previous_selection = (
            st.session_state.selected_project
        )

        default_index = 0

        if previous_selection in project_ids:

            default_index = project_ids.index(
                previous_selection
            )

        selected_project_id = st.selectbox(
            "Select your project",
            options=project_ids,
            index=default_index,
            format_func=lambda project_id: (
                project_options[project_id]
            ),
            key="matching_selector"
        )

        st.session_state.selected_project = (
            selected_project_id
        )

        selected_project = projects[
            projects["project_id"] == selected_project_id
        ].iloc[0]

        st.subheader("Selected project")

        project_card(selected_project)

        required_skill_set = matching.split_items(
            selected_project["required_skills"]
        )

        minimum_skills = min(
            2,
            len(required_skill_set)
        )

        minimum_experience = minimum_experience_label(
            selected_project["required_experience"]
        )

        render_html(f"""
        <div class="requirement-box">

            <b>Mandatory matching requirements</b><br>

            ✓ At least {minimum_skills}
            matching required skill(s)<br>

            ✓ Minimum {safe(minimum_experience)}
            of experience<br>

            ✓ At least
            {safe(selected_project["hours_per_week"])}
            available hours per week

        </div>
        """)

        if st.button(
            "Find AI collaborators",
            type="primary",
            icon=":material/auto_awesome:"
        ):

            st.session_state.recommendation_project = (
                selected_project_id
            )

        if (
            st.session_state.recommendation_project
            == selected_project_id
        ):

            try:

                with st.spinner(
                    "Analyzing candidate compatibility..."
                ):

                    recommendations = (
                        matching.recommend_collaborators(
                            selected_project_id,
                            top_n=3,
                            verbose=False,
                            mandatory_filters=True
                        )
                    )

            except (ValueError, KeyError) as error:

                st.error(
                    f"Unable to generate recommendations: "
                    f"{error}"
                )

                recommendations = None

            if recommendations is not None:

                st.divider()

                st.header("Recommended collaborators")

                if recommendations.empty:

                    empty_state(
                        "No suitable collaborators found",
                        "None of the current profiles satisfy "
                        "all mandatory project requirements. "
                        "Review the requirements or wait "
                        "for additional profiles."
                    )

                else:

                    st.caption(
                        f"Showing {len(recommendations)} "
                        "eligible recommendation(s), "
                        "ranked by compatibility."
                    )

                    if len(recommendations) < 3:

                        st.info(
                            "Fewer than three candidates "
                            "meet all mandatory requirements."
                        )

                    columns = st.columns(
                        len(recommendations)
                    )

                    for i, (_, candidate) in enumerate(
                        recommendations.iterrows()
                    ):

                        with columns[i]:

                            recommendation_card(
                                candidate,
                                i + 1,
                                required_skill_set
                            )

                            with st.expander(
                                "View match details"
                            ):

                                st.markdown(
                                    "#### Compatibility breakdown"
                                )

                                factors = [
                                    (
                                        "Text similarity",
                                        "text_similarity",
                                        30
                                    ),
                                    (
                                        "Skill compatibility",
                                        "skill_match",
                                        25
                                    ),
                                    (
                                        "Interest compatibility",
                                        "interest_match",
                                        10
                                    ),
                                    (
                                        "Availability",
                                        "availability_match",
                                        10
                                    ),
                                    (
                                        "Role compatibility",
                                        "role_match",
                                        10
                                    ),
                                    (
                                        "Experience compatibility",
                                        "experience_match",
                                        10
                                    ),
                                    (
                                        "Collaboration mode",
                                        "collaboration_match",
                                        5
                                    )
                                ]

                                for label, column, weight in factors:

                                    value = float(
                                        candidate[column]
                                    )

                                    st.write(
                                        f"**{label}:** "
                                        f"{value * 100:.1f}%"
                                    )

                                    st.progress(
                                        max(
                                            0.0,
                                            min(1.0, value)
                                        )
                                    )

                                    st.caption(
                                        f"Scoring weight: {weight}%"
                                    )

                                st.divider()

                                st.write(
                                    "**Years of experience:** "
                                    f"{experience_label(candidate['experience'])}"
                                )

                                st.write(
                                    "**Minimum required experience:** "
                                    f"{minimum_experience}"
                                )

                                st.write(
                                    "**All candidate skills:**"
                                )

                                render_html(
                                    skill_tags(
                                        candidate["skills"]
                                    )
                                )

                                st.write(
                                    "**Interests:** "
                                    f"{candidate['interests']}"
                                )

                                st.caption(
                                    "The match score represents "
                                    "weighted compatibility, "
                                    "not the probability of "
                                    "successful collaboration."
                                )

                    st.divider()

                    st.caption(
                        "AI recommendations support human "
                        "decision-making. The project creator "
                        "makes the final collaborator selection."
                    )


# ==========================================
# 13. ABOUT COFOUND PAGE
# ==========================================

elif page == "About CoFound":

    page_header(
        "About CoFound",
        "Intelligence behind the connection",
        "Understand how CoFound evaluates compatibility "
        "and generates collaborator recommendations."
    )

    render_html("""
    <div class="hero">

        <div class="eyebrow">
            EXPLAINABLE ARTIFICIAL INTELLIGENCE
        </div>

        <h1>
            Matching beyond
            <span class="hero-highlight">
                keywords.
            </span>
        </h1>

        <p>
            CoFound combines text similarity,
            structured compatibility factors
            and mandatory eligibility requirements
            to recommend suitable collaborators.
        </p>

    </div>
    """)

    st.header("How the AI works")

    workflow = [
        (
            "01",
            "Input data",
            "Collect project requirements and "
            "collaborator profile information."
        ),
        (
            "02",
            "TF-IDF",
            "Transform textual information into "
            "numerical feature vectors."
        ),
        (
            "03",
            "Cosine similarity",
            "Measure textual similarity between "
            "the project and user profiles."
        ),
        (
            "04",
            "Weighted scoring",
            "Combine seven compatibility factors "
            "into a final match score."
        ),
        (
            "05",
            "Mandatory filters",
            "Exclude candidates who do not meet "
            "minimum project requirements."
        ),
        (
            "06",
            "Ranked recommendations",
            "Return up to three eligible candidates "
            "with the highest compatibility scores."
        )
    ]

    columns = st.columns(3)

    for i, (number, title, description) in enumerate(
        workflow
    ):

        with columns[i % 3]:

            render_html(f"""
            <div class="content-card">

                <div class="stat-icon">
                    {number}
                </div>

                <div class="section-title">
                    {title}
                </div>

                <div class="section-description">
                    {description}
                </div>

            </div>
            """)

    st.divider()

    st.header("Weighted compatibility model")

    weights = pd.DataFrame({
        "Matching factor": [
            "Text similarity",
            "Skill compatibility",
            "Interest compatibility",
            "Availability",
            "Role compatibility",
            "Experience",
            "Collaboration mode"
        ],
        "Weight (%)": [
            30, 25, 10, 10, 10, 10, 5
        ]
    })

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.subheader("Scoring weights")

            st.dataframe(
                weights,
                hide_index=True,
                width="stretch"
            )

    with col2:

        with st.container(border=True):

            st.subheader("Factor importance")

            st.bar_chart(
                weights.set_index("Matching factor"),
                color="#6D4AFF",
                horizontal=True
            )

    st.subheader("Final matching formula")

    st.latex(
        r"""
        S = 100 \times (
        0.30T + 0.25K + 0.10I +
        0.10A + 0.10R + 0.10E + 0.05C)
        """
    )

    st.caption(
        "T = Text similarity, K = Skills, "
        "I = Interests, A = Availability, "
        "R = Role, E = Experience, "
        "C = Collaboration mode."
    )

    st.divider()

    st.header("Mandatory eligibility requirements")

    filters = [
        (
            "◇",
            "Required skills",
            "At least two matching required skills, "
            "or one when the project requires only one."
        ),
        (
            "↗",
            "Years of experience",
            "Candidates must meet or exceed "
            "the minimum required experience."
        ),
        (
            "◷",
            "Availability",
            "Candidates must have enough available "
            "hours to meet the weekly commitment."
        )
    ]

    columns = st.columns(3)

    for i, (icon, title, description) in enumerate(
        filters
    ):

        with columns[i]:

            render_html(f"""
            <div class="content-card">

                <div class="stat-icon">
                    {icon}
                </div>

                <div class="section-title">
                    {title}
                </div>

                <div class="section-description">
                    {description}
                </div>

            </div>
            """)

    st.divider()

    st.header("Experience compatibility")

    experience_table = pd.DataFrame({
        "Profile experience": [
            "0–1 years",
            "2–4 years",
            "5+ years"
        ],
        "Minimum project requirement": [
            "0 years",
            "2 years",
            "5 years"
        ]
    })

    st.dataframe(
        experience_table,
        hide_index=True,
        width="stretch"
    )

    st.caption(
        "Experience is represented using three year ranges. "
        "The current AI model compares ordered experience "
        "categories rather than exact numerical years."
    )

    st.divider()

    st.header("Matching method comparison")

    comparison = pd.DataFrame({
        "Feature": [
            "Skill overlap",
            "TF-IDF",
            "Cosine similarity",
            "Weighted compatibility",
            "Mandatory filters"
        ],
        "Baseline": [
            "Yes", "No", "No", "No", "No"
        ],
        "Original AI": [
            "Yes", "Yes", "Yes", "Yes", "No"
        ],
        "Improved AI": [
            "Yes", "Yes", "Yes", "Yes", "Yes"
        ]
    })

    st.dataframe(
        comparison,
        hide_index=True,
        width="stretch"
    )

    st.divider()

    st.header("Responsible AI and limitations")

    with st.container(border=True):

        st.markdown("""
        - The initial dataset contains synthetic profiles
          rather than verified real users.

        - Matching weights are manually defined
          prototype assumptions.

        - Exact skill matching may not recognize
          equivalent skills or alternative terminology.

        - Experience is represented by predefined year
          ranges rather than exact numerical years.

        - Location is stored but is not currently
          included in the matching score.

        - Collaboration preferences influence ranking
          but are not mandatory requirements.

        - Recommendations do not guarantee
          successful collaboration.

        - The application uses local CSV storage
          without authentication or private accounts.

        - Final collaborator selection remains
          a human decision.
        """)


# ==========================================
# 14. FOOTER
# ==========================================

render_html("""
<div class="footer">

    <b>cofound.</b>
    — Connect. Collaborate. Create.<br>

    AI Project & Collaborator Matching Platform<br>

    Introduction to Artificial Intelligence · 2026/2027

</div>
""")