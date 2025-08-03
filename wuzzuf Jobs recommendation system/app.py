import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from recommender import load_data, recommend_jobs
import re
from collections import Counter

# Page config
st.set_page_config(page_title="Wuzzuf Job Recommender", layout="wide")

# CSS for clickable buttons
st.markdown("""
    <style>
    button[kind="primary"], button[kind="secondary"] {
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def get_data():
    return load_data()

df = get_data()

# Sidebar navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.selectbox("Choose Page", ["Recommender", "Visual Insights"])

# ----------------- Recommender Page -----------------
if page == "Recommender":
    st.title("🔍 Job Recommendation System – Wuzzuf")

    with st.container():
        st.subheader("📋 Select your preferences:")

        col1, col2 = st.columns(2)
        with col1:
            city = st.selectbox("City", sorted(df["City"].dropna().unique()))
            job_type = st.selectbox("Job Type", sorted(df["Job Type"].dropna().unique()))
        with col2:
            work_mode = st.selectbox("Work Mode", sorted(df["Work Mode"].dropna().unique()))

            def extract_min_exp(val):
                if pd.isna(val) or not isinstance(val, str):
                    return 0
                nums = re.findall(r"\d+", val)
                return int(nums[0]) if nums else 0

            exp_values = sorted({extract_min_exp(v) for v in df["Experience"].dropna()})
            min_exp = st.selectbox("Minimum Years of Experience", exp_values)

        user_input_skills = st.text_area("🧠 Enter your skills (e.g. Python, Power BI, SQL)", height=100)
        recommend = st.button("🔎 Recommend Jobs")

    if recommend:
        if all([city, job_type, work_mode, user_input_skills.strip()]):
            try:
                results = recommend_jobs(df, user_input_skills, city, job_type, work_mode, int(min_exp))
                if not results.empty:
                    # Make links clickable
                    results["Link"] = results["Link"].apply(
                        lambda x: f'<a href="{x}" target="_blank">Apply Here</a>'
                    )

                    st.success("✅ Found job recommendations based on your profile:")
                    st.markdown(results.to_html(escape=False, index=False), unsafe_allow_html=True)

                    # Explanation
                    st.info(
                        "ℹ️ These recommendations are based on the similarity between "
                        "your entered skills and the job's required skills using TF-IDF "
                        "and cosine similarity. Higher match scores indicate stronger skill alignment."
                    )

                    # Balloons animation
                    st.balloons()

                else:
                    st.warning("⚠️ No matching jobs found. Try adjusting your filters.")
            except Exception as e:
                st.error(f"❌ An error occurred during recommendation: {e}")
        else:
            st.error("❌ Please fill out all fields before clicking Recommend.")

# ----------------- Visual Insights Page -----------------
elif page == "Visual Insights":
    st.title("📊 Visual Insights from Wuzzuf Dataset")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Cities by Job Count")
        city_counts = df["City"].value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=city_counts.values, y=city_counts.index, ax=ax, palette="Blues_d")
        ax.set_xlabel("Job Count")
        ax.set_ylabel("City")
        st.pyplot(fig)

    with col2:
        st.subheader("Top 10 Job Titles by Count")
        job_titles = df["Job Title"].value_counts().head(10)
        fig2, ax2 = plt.subplots()
        sns.barplot(x=job_titles.values, y=job_titles.index, ax=ax2, palette="Greens_d")
        ax2.set_xlabel("Job Count")
        ax2.set_ylabel("Job Title")
        st.pyplot(fig2)

    st.subheader("Top Required Skills (based on TF-IDF cleaned data)")
    all_skills = df["Cleaned_Skills"].dropna().str.split().sum()
    skill_freq = Counter(all_skills)
    top_skills = pd.DataFrame(skill_freq.most_common(15), columns=["Skill", "Frequency"])
    st.bar_chart(top_skills.set_index("Skill"))
