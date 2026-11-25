# CoFound – AI Project & Collaborator Matching Platform

**Student:** Emilija Mitevska  
**Student ID:** 131766  
**Course:** Introduction to Artificial Intelligence  

## 1. Project Overview

CoFound is an AI-powered web platform designed to help people find suitable collaborators for their projects.

The system analyzes project requirements and user profiles to recommend potential collaborators based on their skills, interests, experience, availability, preferred roles, and collaboration preferences.

CoFound combines content-based recommendation techniques with mandatory eligibility filters to provide more suitable and reliable recommendations.

## 2. Problem Description

Finding suitable collaborators can be difficult, especially when a project requires specific technical skills, professional experience, and time commitment.

CoFound aims to simplify this process by automatically identifying and ranking candidates whose profiles match project requirements.

The platform is intended for students, developers, designers, entrepreneurs, freelancers, and other professionals interested in project collaboration.

## 3. Main Features

The current web application includes:

- Overview dashboard with dataset statistics.
- Community page for browsing and filtering user profiles.
- Creation of new user profiles.
- Project browsing and category filtering.
- Creation of new projects.
- AI-powered collaborator recommendations.
- Individual matching scores and explanations.
- Mandatory eligibility validation.
- Experience displayed in years-based ranges.
- Feedback when no suitable collaborators are available.

The application currently uses CSV-based data storage.

## 4. AI Methodology

CoFound uses a content-based recommendation approach.

### TF-IDF

Term Frequency–Inverse Document Frequency converts project descriptions, required skills, and user profile information into numerical vectors.

### Cosine Similarity

Measures textual similarity between project requirements and candidate profiles.

### Weighted Matching

The final matching score combines seven factors:

| Matching Factor | Weight |
|---|---:|
| Text similarity | 30% |
| Skill matching | 25% |
| Interest matching | 10% |
| Availability matching | 10% |
| Role matching | 10% |
| Experience matching | 10% |
| Collaboration preference | 5% |
| Total | 100% |

Final Score = 100 × (0.30 × Text Similarity + 0.25 × Skill Match + 0.10 × Interest Match + 0.10 × Availability Match + 0.10 × Role Match + 0.10 × Experience Match + 0.05 × Collaboration Match)

The weights are manually defined rather than learned through model training.

### Mandatory Eligibility Filters

Before a candidate can be recommended, they must:

- Match at least two required skills, or all required skills if fewer than two are specified.
- Meet the minimum experience requirement.
- Have sufficient weekly availability.

Eligible candidates are ranked according to their final matching scores.

The system returns up to three recommendations per project. If no eligible candidates are available, the system displays an appropriate message.

Matching scores represent weighted compatibility scores, not probabilities of successful collaboration.

## 5. Dataset

The dataset was progressively expanded during development.

| Development Stage | Users | Projects |
|---|---:|---:|
| Initial prototype | 5 | 2 |
| Expanded prototype | 40 | 10 |
| Current version | 200 | 30 |

The current dataset contains 6,000 possible user–project combinations.

### User Profiles

File: `data/user_profiles.csv`

Each user profile includes:

- User ID and name
- Skills and interests
- Experience level
- Weekly availability
- Preferred professional role
- Preferred project types
- Collaboration mode
- Location

### Projects

File: `data/projects.csv`

Each project includes:

- Project ID and title
- Project description
- Required skills
- Project category
- Required professional role
- Minimum experience
- Required weekly availability
- Collaboration mode
- Location

The dataset contains synthetic profiles and projects created for development, testing, and experimental evaluation.

## 6. Experimental Evaluation

Three recommendation methods were compared using the same dataset and evaluation criteria.

- Baseline: Simple skill-overlap matching.
- Original AI: TF-IDF, cosine similarity, and weighted ranking.
- Improved AI: Weighted ranking with mandatory eligibility filters.

The evaluation dataset contains 178 eligible and 5,822 ineligible user–project combinations.

### Evaluation Results

| Metric | Baseline | Original AI | Improved AI |
|---|---:|---:|---:|
| Precision@3 | 0.389 | 0.533 | 0.767 |
| Recall@3 | 0.343 | 0.503 | 0.688 |
| MRR | 0.500 | 0.717 | 0.967 |
| NDCG@3 | 0.450 | 0.657 | 1.000 |
| Recommendation validity | 38.89% | 53.33% | 100% |
| Project coverage | 100% | 100% | 96.67% |

### Recommendation Quality

| Result | Baseline | Original AI | Improved AI |
|---|---:|---:|---:|
| Total recommendations | 90 | 90 | 69 |
| Valid recommendations | 35 | 48 | 69 |
| Invalid recommendations | 55 | 42 | 0 |
| Projects covered | 30 | 30 | 29 |

The improved method increased recommendation validity and eliminated invalid recommendations under the defined eligibility criteria.

Evaluation labels are generated using predefined eligibility rules. Therefore, these results measure eligibility compliance rather than independently verified real-world recommendation quality.

## 7. Error Analysis

| Error Type | Baseline | Original AI | Improved AI |
|---|---:|---:|---:|
| Insufficient skills | 0 | 1 | 0 |
| Insufficient experience | 25 | 11 | 0 |
| Insufficient availability | 52 | 35 | 0 |
| Total invalid recommendations | 55 | 42 | 0 |

Insufficient availability was the most common reason for invalid recommendations.

Individual error counts may overlap because a candidate can fail multiple requirements.

Detailed experimental results are stored in the `data` and `experiments` folders.

## 8. Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- HTML and CSS
- CSV data storage
- Google Sheets
- Visual Studio Code
- Git and GitHub

## 9. Project Structure

    CoFound/
    ├── assets/
    │   ├── logo.svg
    │   └── styles.css
    ├── .streamlit/
    │   └── config.toml
    ├── data/
    │   ├── user_profiles.csv
    │   ├── projects.csv
    │   ├── evaluation_labels.csv
    │   └── comparison_results.csv
    ├── experiments/
    │   ├── experiment_summary.csv
    │   ├── recommendation_quality.csv
    │   ├── error_analysis.csv
    │   └── error_summary.csv
    ├── docs/
    │   └── test_log.csv
    ├── app.py
    ├── matching.py
    ├── baseline.py
    ├── generate_dataset.py
    ├── create_evaluation.py
    ├── compare_methods.py
    ├── error_analysis.py
    ├── requirements.txt
    └── README.md

The structure above shows the main project files and folders.

## 10. Installation and Execution

### Step 1 – Clone the Repository

```powershell
git clone https://github.com/emitevska/CoFound.git
cd CoFound
```

### Step 2 – Install Dependencies

Make sure Python is installed.

```powershell
py -m pip install -r requirements.txt
```

### Step 3 – Run the Web Application

```powershell
py -m streamlit run app.py
```

The application will open in a web browser.

### Run the Matching Algorithm

```powershell
py matching.py
```

### Reproduce the Experimental Evaluation

Using the original evaluation dataset of 200 users and 30 projects, run:

```powershell
py create_evaluation.py
py compare_methods.py
py error_analysis.py
```

These scripts regenerate the evaluation labels, comparison results, and error analysis.

On systems where the `py` launcher is unavailable, use `python` instead.

## 11. Testing and Evidence

Basic functional testing was performed for:

- User profile creation.
- Project creation.
- Input validation.
- Profile and project search.
- Filtering functionality.
- AI recommendation generation.
- Mandatory eligibility filters.
- No-match scenarios.
- Data persistence after refreshing the application.

The test results are documented in `docs/test_log.csv`.

Temporary test profiles and projects were removed by restoring the original evaluation dataset after testing.

Full system verification will be performed during the final development stage.

## 12. Current Limitations

- The dataset contains synthetic rather than real-world profiles.
- Evaluation labels are based on predefined eligibility rules.
- Matching weights are manually selected.
- Skill matching relies on exact normalized skill names.
- Experience is represented through categories displayed as years-based ranges.
- Location is stored but is not currently included in the matching score.
- The application currently uses CSV files instead of a database.
- User authentication and individual account management are not yet implemented.
- Independent human evaluation is still required.

## 13. Ethical Considerations

CoFound is designed to support human decision-making rather than automatically select collaborators.

The application provides matching scores and explanations to help users understand the recommendations.

Synthetic data is used during development and evaluation to reduce privacy risks. Recommendations do not guarantee successful collaboration, and the final decision remains with the user.

## 14. Next Steps

The next development objectives are:

1. Implement user registration and login.
2. Integrate an SQLite database.
3. Introduce personal profile management.
4. Introduce personal project management.
5. Improve application security and access control.
6. Refactor and improve the application code.
7. Conduct additional recommendation validation.
8. Improve the user interface and overall usability.

## 15. Project Status

**Current stage:** Functional AI-powered web application prototype.

The expanded dataset, improved recommendation algorithm, web interface, experimental evaluation, error analysis, and basic functional testing are completed.

Authentication, database integration, additional validation, and final system verification remain planned for the next development stages.
