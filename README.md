# AI-Based Resume Screening & Job Recommendation System

A Flask-based web application that automates resume screening using **Natural Language Processing (NLP)** and **Machine Learning (TF-IDF + Cosine Similarity)**. The system extracts skills from uploaded resumes, compares them against job descriptions, calculates resume scores, and recommends the most relevant jobs.

---

# Features

- User Registration & Login
- Resume Upload (PDF & DOCX)
- Resume Parsing
- NLP-Based Skill Extraction
- TF-IDF Job Recommendation Engine
- Resume Scoring
- Admin Dashboard
- Automatic Model Retraining
- Responsive Web Interface

---

# System Workflow

```
Resume Upload
      │
      ▼
Resume Parser
(PDF / DOCX → Text)
      │
      ▼
NLP Processing
(Text Cleaning & Tokenization)
      │
      ▼
Skill Extraction
      │
      ▼
TF-IDF Vectorization
      │
      ▼
Cosine Similarity
      │
      ▼
Resume Score + Job Recommendations
```

---

# Modules Implemented

| Module | Description |
|---------|-------------|
| User Authentication | User Registration & Login |
| Resume Upload | Upload resumes in PDF or DOCX format |
| Resume Parser | Extracts text from uploaded resumes |
| Skill Extraction | NLP-based technical skill detection |
| Job Recommendation | TF-IDF + Cosine Similarity matching |
| Resume Scoring | Calculates skill match percentage |
| Admin Module | Add, edit, delete job postings |

---

# Technologies Used

## Backend

- Python
- Flask

## Machine Learning

- Scikit-learn
- TF-IDF Vectorizer
- Cosine Similarity

## NLP

- NLTK

## Data Processing

- Pandas
- NumPy

## Resume Parsing

- pdfplumber
- python-docx

## Frontend

- HTML
- CSS
- JavaScript
- Jinja2 Templates

---

# Installation

## 1. Clone the repository

```bash
git clone <repository-url>
cd AI_Resume_Screening_System
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Recommended Python Version:** 3.11 or 3.12

Python 3.14 is not currently recommended because some dependencies (such as Pandas) may require manual compilation.

---

## 4. Download NLTK Data

Run once:

```bash
python -m nltk.downloader punkt punkt_tab stopwords
```

or

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

---

## 5. Train the Recommendation Model

```bash
python model/train_model.py
```

This generates:

```
model/vectorizer.pkl
model/job_vectors.pkl
```

If these files already exist, retraining is only required after modifying the job dataset.

---

## 6. Run the Application

```bash
python app.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

# Default Admin Account

| Email | Password |
|--------|----------|
| admin@resume.ai | admin123 |

Users can also create their own accounts using the Register page.

---

# Machine Learning Pipeline

### Resume Parser

- Extracts text from PDF and DOCX resumes.

### Skill Extraction

- Cleans text using NLP.
- Tokenizes resume content.
- Removes stopwords.
- Matches technical skills against a predefined skills database.

### Job Recommendation

- TF-IDF Vectorizer converts job skills into numerical vectors.
- Resume skills are transformed using the same vectorizer.
- Cosine Similarity ranks jobs according to relevance.

### Resume Score

For each recommended job:

```
Resume Score =
(Matched Skills / Required Skills) × 100
```

Both the resume score and cosine similarity percentage are displayed.

---

# Admin Dashboard

Administrators can:

- Add new jobs
- Edit jobs
- Delete jobs
- View registered users

Whenever a job is modified, the TF-IDF model is automatically retrained.

---

# Storage

## Users

Stored in:

```
database/users.json
```

through a lightweight abstraction layer.

## Jobs

Stored in:

```
model/job_data.csv
```

---

# Project Structure

```
AI_Resume_Screening_System/
│
├── app.py
├── requirements.txt
├── README.md
│
├── config/
│   └── database.py
│
├── model/
│   ├── train_model.py
│   ├── job_data.csv
│   ├── vectorizer.pkl
│   └── job_vectors.pkl
│
├── utils/
│   ├── resume_parser.py
│   ├── skill_extractor.py
│   └── recommendation.py
│
├── uploads/
│   └── resumes/
│
├── database/
│   └── users.json
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── upload_resume.html
│   ├── login.html
│   ├── register.html
│   ├── result.html
│   └── admin.html
│
└── static/
    ├── css/
    └── js/
```

---

# Testing

The application has been tested with:

- User Registration
- User Login
- PDF Resume Upload
- DOCX Resume Upload
- Resume Parsing
- Skill Extraction
- Job Recommendation
- Resume Scoring
- Admin Job Management
- Automatic Model Retraining

---

# Future Improvements

- AI Interview Question Generator
- LLM-Based Resume Analysis
- Resume Feedback & Suggestions
- LinkedIn Profile Integration
- Salary Prediction
- Email Notifications
- Video Resume Analysis
- MongoDB Integration
- REST API
- Docker Deployment

---

# License

This project is intended for educational and academic purposes.