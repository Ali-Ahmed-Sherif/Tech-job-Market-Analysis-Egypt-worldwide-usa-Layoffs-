import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import clean_skills

def load_data():
    df = pd.read_excel("Cleaned_Dataset_for_taison.xlsx", sheet_name="Fact_Wuzzuf")
    df["Cleaned_Skills"] = df["Skills"].fillna("").apply(clean_skills)
    return df

def recommend_jobs(df, user_input_skills, city, job_type, work_mode, min_experience):
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df["Cleaned_Skills"].fillna(""))

    user_cleaned = clean_skills(user_input_skills)
    user_vec = tfidf.transform([user_cleaned])

    # Filter based on dropdowns
    filtered_df = df[
        (df["City"].str.lower() == city.lower()) &
        (df["Job Type"].str.lower() == job_type.lower()) &
        (df["Work Mode"].str.lower() == work_mode.lower())
    ].copy()

    # Filter by experience
    def extract_min_exp(val):
        if pd.isna(val) or not isinstance(val, str):
            return 0
        numbers = re.findall(r"\d+", val)
        return int(numbers[0]) if numbers else 0

    filtered_df = filtered_df[filtered_df["Experience"].apply(extract_min_exp) >= min_experience]
    filtered_df = filtered_df.reset_index(drop=True)

    if filtered_df.empty:
        return pd.DataFrame()

    filtered_tfidf = tfidf_matrix[filtered_df.index]
    similarities = cosine_similarity(user_vec, filtered_tfidf).flatten()
    filtered_df["Match Score"] = (similarities * 100).round(2)

    top_matches = (
        filtered_df
        .sort_values(by="Match Score", ascending=False)
        .drop_duplicates(subset=["Job Title", "Job Position", "Company", "Link"])
        .head(3)
    )

    return top_matches[[
        "Job Position", "Company", "CompanyLocation",
        "City", "Job Type", "Work Mode",  "Skills", "Match Score", "Link"
    ]]
