"""
model/train_model.py
----------------------
Module 5 (training step): Job Recommendation System

Builds a TF-IDF vectorizer over the job skills corpus (model/job_data.csv)
and pre-computes job vectors, so that at request-time we only need to
transform the candidate's extracted skills and run cosine similarity -
no retraining needed per request.

Run this script whenever model/job_data.csv changes:
    python model/train_model.py

Saves:
    model/vectorizer.pkl   -> fitted TfidfVectorizer
    model/job_vectors.pkl  -> TF-IDF matrix for all jobs in job_data.csv
"""

import os
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_DATA_PATH = os.path.join(BASE_DIR, "job_data.csv")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
JOB_VECTORS_PATH = os.path.join(BASE_DIR, "job_vectors.pkl")


def train():
    jobs = pd.read_csv(JOB_DATA_PATH)
    jobs["skills"] = jobs["skills"].fillna("")

    vectorizer = TfidfVectorizer()
    job_vectors = vectorizer.fit_transform(jobs["skills"])

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(job_vectors, JOB_VECTORS_PATH)

    print(f"Trained TF-IDF vectorizer on {len(jobs)} jobs.")
    print(f"Saved -> {VECTORIZER_PATH}")
    print(f"Saved -> {JOB_VECTORS_PATH}")


if __name__ == "__main__":
    train()
