import streamlit as st
from news_fetcher import fetch_top_headlines
from summarizer import load_summarizer, summarize_text
from quiz_maker import load_quiz_model, generate_quiz
from datetime import datetime

# -------------------------------
# Load models (cached)
# -------------------------------
@st.cache_resource
def load_models():
    summarizer = load_summarizer()
    quiz = load_quiz_model()
    return summarizer, quiz

(tokenizer, summary_model), (_, quiz_model) = load_models()

# -------------------------------
# Streamlit setup
# -------------------------------
st.set_page_config(page_title="📰 News Summarizer & Quiz Maker", layout="wide")

# -------------------------------
# Session state initialization
# -------------------------------
if "articles" not in st.session_state:
    st.session_state.articles = []
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "page" not in st.session_state:
    st.session_state.page = "main"

# -------------------------------
# MAIN PAGE
# -------------------------------
if st.session_state.page == "main":
    st.title("📰 Real-Time News Summarizer & Quiz Maker")
    st.caption("Fetch latest headlines, summarize with BART, and create MCQs using Gemini 2.5 Flash.")

    # Sidebar
    st.sidebar.header("⚙️ Settings")
    country = st.sidebar.selectbox("🌍 Country", ["in", "us", "gb", "au", "ca"])
    category = st.sidebar.selectbox(
        "🗂️ Category",
        ["general", "technology", "business", "entertainment", "health", "science", "sports"]
    )
    num_articles = st.sidebar.slider("📰 Number of Articles", 1, 10, 3)

    # Fetch + summarize
    if st.button("🚀 Fetch & Summarize"):
        st.info("Fetching latest news...")
        articles = fetch_top_headlines(country, category, page_size=num_articles)
        st.session_state.articles = articles
        st.session_state.summaries = []
        st.session_state.quiz_data = []

        if not articles:
            st.error("No articles found or API limit reached.")
        else:
            st.success(f"✅ Fetched {len(articles)} articles successfully!")
            for i, article in enumerate(articles, start=1):
                with st.container():
                    title = article.get("title", "No title")
                    source = article.get("source", "Unknown")
                    url = article.get("url", "#")
                    content = article.get("content", "")

                    st.markdown(f"### 🗞️ {i}. {title}")
                    st.markdown(f"**📰 Source:** {source}")
                    st.markdown(f"🔗 [Read full article]({url})")

                    st.markdown("⏳ Generating summary...")
                    summary = summarize_text(tokenizer, summary_model, content)
                    st.session_state.summaries.append(summary)

                    st.markdown("#### 🧠 Summary:")
                    st.success(summary)
                    st.markdown("---")

            st.success("✅ All summaries generated successfully!")

    # 👇 Restore summaries if coming back from quiz
    if st.session_state.get("show_summary_again", False):
        st.success("👋 Welcome back! Here are your previous summaries:")
        for i, (article, summary) in enumerate(zip(st.session_state.articles, st.session_state.summaries), start=1):
            title = article.get("title", "No title")
            st.markdown(f"### 🗞️ {i}. {title}")
            st.markdown("#### 🧠 Summary:")
            st.info(summary)
            st.markdown("---")
        st.session_state.show_summary_again = False

    # Generate quiz button
    if st.session_state.summaries:
        st.markdown("---")
        if st.button("🧩 Generate Quiz for All Summaries"):
            st.session_state.page = "quiz"
            st.query_params["page"] = "quiz"  # Updated API
            st.rerun()

# -------------------------------
# QUIZ PAGE
# -------------------------------
elif st.session_state.page == "quiz":
    st.title("🧠 Quiz Time!")
    st.caption("Generated using Gemini 2.5 Flash from your summarized news.")

    # ✅ Generate quiz data if not already done
    if not st.session_state.quiz_data:
        with st.spinner("Generating quiz questions... ⏳"):
            quiz_list = []
            for summary in st.session_state.summaries:
                quiz = generate_quiz(None, quiz_model, summary, num_questions=3)
                quiz_list.append(quiz)
            st.session_state.quiz_data = quiz_list

    # ✅ Initialize answers state
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    # ---------------------------------
    # 📥 Download quiz as a text file
    # ---------------------------------
    quiz_text_content = "🧠 QUIZ QUESTIONS\n\n"
    q_counter = 1
    for i, quiz_set in enumerate(st.session_state.quiz_data, start=1):
        for q_index, q in enumerate(quiz_set):
            quiz_text_content += f"Q{q_counter}: {q['question']}\n"
            for j, option in enumerate(q["options"], start=0):
                quiz_text_content += f"{chr(65+j)}) {option}\n"
            quiz_text_content += f"Answer: {q['answer']}\n\n"
            q_counter += 1

    st.download_button(
        label="📥 Download Quiz",
        data=quiz_text_content,
        file_name=f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        help="Download the full quiz as a text file"
    )

    # ---------------------------------
    # 📝 Quiz Display
    # ---------------------------------
    st.subheader("📝 Attempt the Quiz")

    q_counter = 1
    for i, quiz_set in enumerate(st.session_state.quiz_data, start=1):
        for q_index, q in enumerate(quiz_set):
            question_id = f"summary_{i}_q_{q_index}"
            st.markdown(f"**Q{q_counter}:** {q['question']}")
            user_choice = st.radio(
                f"Select your answer for Q{q_counter}",
                q["options"],
                key=question_id,
                index=None
            )
            st.session_state.user_answers[question_id] = user_choice
            st.markdown("---")
            q_counter += 1

    # ---------------------------------
    # ✅ Submit and Show Results
    # ---------------------------------
    if st.button("✅ Submit Quiz"):
        score = 0
        total = 0
        st.markdown("## 🏁 Results")

        q_counter = 1
        for i, quiz_set in enumerate(st.session_state.quiz_data, start=1):
            for q_index, q in enumerate(quiz_set):
                question_id = f"summary_{i}_q_{q_index}"
                user_answer = st.session_state.user_answers.get(question_id, None)
                correct_answer = q["answer"].strip().upper()

                correct_option_index = ord(correct_answer) - 65 if correct_answer in ["A", "B", "C", "D"] else None
                correct_text = q["options"][correct_option_index] if correct_option_index is not None else "Unknown"

                total += 1
                if user_answer == correct_text:
                    score += 1
                    st.success(f"✅ Q{q_counter}: Correct! ({correct_answer})")
                else:
                    st.error(f"❌ Q{q_counter}: Incorrect. Correct answer is **{correct_answer}) {correct_text}**")

                q_counter += 1

        st.markdown(f"### 🧮 Your Score: **{score} / {total}**")

    # ---------------------------------
    # 🔙 Back Button (no refresh)
    # ---------------------------------
    if st.button("🔙 Back to Summarizer"):
        st.session_state.page = "main"
        st.session_state.user_answers = {}
        st.query_params["page"] = "main"  # ✅ Updated, no deprecation warning
        st.session_state.show_summary_again = True
