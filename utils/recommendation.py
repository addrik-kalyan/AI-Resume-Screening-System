"""
utils/recommendation.py
--------------------------
Module 5: Job Recommendation System  (TF-IDF + Cosine Similarity)
Module 6: Resume Scoring            (Matched Skills / Required Skills * 100)

If the trained vectorizer/job_vectors are missing, they are trained
automatically on first import so the app works out-of-the-box.
"""

import os
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")
JOB_DATA_PATH = os.path.join(MODEL_DIR, "job_data.csv")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
JOB_VECTORS_PATH = os.path.join(MODEL_DIR, "job_vectors.pkl")


def _ensure_model_trained():
    if not (os.path.exists(VECTORIZER_PATH) and os.path.exists(JOB_VECTORS_PATH)):
        from model.train_model import train
        train()


def _load_jobs():
    jobs = pd.read_csv(JOB_DATA_PATH)
    jobs["skills"] = jobs["skills"].fillna("")
    return jobs


def recommend_jobs(skills, top_n=5):
    """
    Module 5: Recommend jobs using TF-IDF + Cosine Similarity.

    Args:
        skills (list[str]): skills extracted from the candidate's resume
        top_n (int): number of recommendations to return

    Returns:
        list[dict]: [{job, company, description, similarity, match_score,
                      matched_skills, required_skills}, ...] sorted by best match
    """
    _ensure_model_trained()

    vectorizer = joblib.load(VECTORIZER_PATH)
    job_vectors = joblib.load(JOB_VECTORS_PATH)
    jobs = _load_jobs()

    candidate_text = " ".join(skills) if skills else ""
    candidate_vector = vectorizer.transform([candidate_text])

    similarities = cosine_similarity(candidate_vector, job_vectors).flatten()

    results = []
    candidate_skill_set = set(s.lower() for s in skills)

    for idx, row in jobs.iterrows():
        required_skills = [s.strip() for s in row["skills"].split() if s.strip()]
        # required_skills above splits single tokens; better: split by the
        # original comma-free space-separated phrase list defined in CSV.
        required_skills = _split_required_skills(row["skills"])

        matched = [s for s in required_skills if s.lower() in candidate_text.lower()]
        match_score = score_resume(matched, required_skills)

        results.append({
            "job": row["job"],
            "company": row["company"],
            "description": row.get("description", ""),
            "similarity": round(float(similarities[idx]) * 100, 1),
            "match_score": match_score,
            "matched_skills": matched,
            "required_skills": required_skills,
        })

    # Rank primarily by TF-IDF cosine similarity (core ML ranking signal)
    results.sort(key=lambda r: r["similarity"], reverse=True)

    # Only keep jobs with at least some signal of relevance
    filtered = [r for r in results if r["similarity"] > 0 or r["match_score"] > 0]
    return (filtered if filtered else results)[:top_n]


def _split_required_skills(skills_str):
    """
    job_data.csv stores skills as a space-separated string where multi-word
    skills (e.g. 'machine learning') are still just space separated.
    We reconstruct known multi-word skills so scoring/matching is accurate.
    """
    from utils.skill_extractor import SKILLS_LIST

    text = skills_str.lower()
    found = []
    remaining = text
    # Greedily extract known multi-word skills first
    for skill in sorted(SKILLS_LIST, key=len, reverse=True):
        if skill in remaining:
            found.append(skill)
            remaining = remaining.replace(skill, " ")
    # Anything left over (skills not in our master list) -> keep as single tokens
    leftover_tokens = [t for t in remaining.split() if t]
    found.extend(leftover_tokens)
    # de-duplicate, preserve order
    seen = set()
    unique = []
    for s in found:
        if s not in seen:
            unique.append(s)
            seen.add(s)
    return unique


def score_resume(matched_skills, required_skills):
    """
    Module 6: Resume Scoring
    Score = (Matched Skills / Required Skills) * 100
    """
    if not required_skills:
        return 0.0
    return round((len(matched_skills) / len(required_skills)) * 100, 1)
