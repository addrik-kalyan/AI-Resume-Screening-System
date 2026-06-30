"""
utils/skill_extractor.py
--------------------------
Module 4: Skill Extraction using NLP

Techniques: Tokenization, text cleaning, keyword extraction.
Uses NLTK for tokenization/stopword removal, then matches tokens (and
multi-word phrases, e.g. "machine learning") against a master skills list.
"""

import re
import nltk

# Ensure required NLTK resources are available.
# Handles both older and newer NLTK versions safely.
REQUIRED_DATA = [
    ("punkt", "tokenizers/punkt"),
    ("stopwords", "corpora/stopwords"),
]

for package, path in REQUIRED_DATA:
    try:
        nltk.data.find(path)
    except (LookupError, OSError):
        nltk.download(package, quiet=True)

# punkt_tab exists only in newer NLTK versions.
try:
    nltk.download("punkt_tab", quiet=True)
except Exception:
    pass

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    STOPWORDS = set(stopwords.words("english"))

# Master skills list. Multi-word skills are matched as phrases.
SKILLS_LIST = [
    "python", "java", "c++", "c", "javascript", "typescript", "react",
    "react native", "angular", "vue", "node.js", "express", "flask",
    "django", "spring", "hibernate", "mongodb", "mysql", "postgresql",
    "oracle", "sql", "nosql", "aws", "azure", "gcp", "docker", "kubernetes",
    "terraform", "jenkins", "ci/cd", "linux", "windows server", "bash",
    "networking", "git", "rest api", "graphql", "machine learning",
    "deep learning", "data science", "data analysis", "statistics",
    "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "nlp",
    "spacy", "nltk", "transformers", "tableau", "power bi", "excel",
    "html", "css", "figma", "adobe xd", "wireframing", "prototyping",
    "android", "kotlin", "flutter", "dart", "selenium", "testing",
    "automation", "penetration testing", "network security", "firewalls",
    "database administration", "communication", "requirement analysis",
    "mobile development", "research", "shell scripting",
]


def _clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\.\s\-/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text):
    """
    Find skills present in resume text.
    Returns: list[str] of matched skills.
    """
    cleaned = _clean_text(text)

    try:
        tokens = [t for t in word_tokenize(cleaned) if t not in STOPWORDS]
    except LookupError:
        try:
            nltk.download("punkt", quiet=True)
            tokens = [t for t in word_tokenize(cleaned) if t not in STOPWORDS]
        except Exception:
            tokens = cleaned.split()

    found = []

    for skill in SKILLS_LIST:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, cleaned):
            found.append(skill)

    return found