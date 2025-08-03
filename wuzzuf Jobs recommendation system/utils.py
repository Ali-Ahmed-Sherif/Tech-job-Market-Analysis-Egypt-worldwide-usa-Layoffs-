import re
import pandas as pd

manual_stopwords = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for',
    'if', 'in', 'into', 'is', 'it', 'no', 'not', 'of', 'on', 'or',
    'such', 'that', 'the', 'their', 'then', 'there', 'these', 'they',
    'this', 'to', 'was', 'will', 'with', 'you', 'your'
}

lemmatization_dict = {
    "analyzing": "analysis",
    "analysing": "analysis",
    "analysts": "analyst",
    "dashboards": "dashboard",
    "databases": "database",
    "scripts": "script",
    "technologies": "technology",
    "tools": "tool",
    "pipelines": "pipeline"
}

def clean_skills(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = text.split()
    tokens = [word for word in tokens if word not in manual_stopwords]
    tokens = [lemmatization_dict.get(word, word) for word in tokens]
    return " ".join(tokens)
