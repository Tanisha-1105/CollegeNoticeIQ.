
import re
import html
import streamlit as st
import spacy

# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="CollegeNoticeIQ",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# 2. LOAD SPACY MODEL
# ==========================================================

@st.cache_resource
def load_nlp():
    return spacy.load("en_core_web_sm")


nlp = load_nlp()


# ==========================================================
# 3. CUSTOM CSS
# ==========================================================

st.markdown("""
<style>
/* Page background and spacing */
.stApp {
    background-color: #f4f7fb;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1500px;
    padding: 0.6rem 1.5rem 0.5rem;
}

/* Main heading */
h1 {
    font-size: 1.8rem !important;
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
    color: #183153;
}

h2, h3 {
    color: #183153;
    font-size: 1.05rem !important;
}

/* Compact notice input */
.stTextArea textarea {
    min-height: 85px !important;
    background-color: #ffffff;
    border: 1px solid #d8e1ee;
    border-radius: 9px;
    font-size: 0.9rem;
}

/* Buttons */
.stButton button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 2.2rem;
}

/* Streamlit bordered containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff;
    border: 1px solid #e0e7f0;
    border-radius: 12px;
    padding: 0.7rem 0.9rem;
    box-shadow: 0 2px 8px rgba(25, 45, 80, 0.04);
}

/* Result labels */
.info-row {
    display: grid;
    grid-template-columns: 105px minmax(0, 1fr);
    gap: 8px;
    padding: 5px 0;
    border-bottom: 1px solid #edf1f6;
    font-size: 0.85rem;
}

.info-label {
    font-weight: 600;
    color: #53657d;
}

.info-value {
    color: #183153;
    overflow-wrap: anywhere;
}

/* Category label */
.category-chip {
    display: inline-block;
    background: #e7efff;
    color: #2454a6;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    margin-bottom: 8px;
}

/* Summary and answer */
.summary-box {
    background: #f1f6ff;
    color: #263e60;
    border-radius: 8px;
    padding: 10px;
    font-size: 0.85rem;
    overflow-wrap: anywhere;
}

.answer-box {
    background: #eaf8ef;
    color: #17663a;
    border-radius: 8px;
    padding: 10px;
    font-size: 0.88rem;
    overflow-wrap: anywhere;
}

/* Small footer */
.footer-text {
    text-align: center;
    font-size: 0.75rem;
    color: #7b8798;
    margin-top: 12px;
}

/* Small screens */
@media (max-width: 900px) {
    .block-container {
        padding: 0.5rem 0.7rem;
    }

    h1 {
        font-size: 1.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# 4. TEXT PREPROCESSING
# ==========================================================

def preprocess_text(text):
    doc = nlp(text.lower())

    tokens = [
        token.text
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
    ]

    return tokens


# ==========================================================
# 5. INFORMATION EXTRACTION
# ==========================================================

def extract_information(text):
    info = {
        "Event": "Not found",
        "Date": "Not found",
        "Time": "Not found",
        "Venue": "Not found",
        "Department": "Not found",
        "Deadline": "Not found",
        "Requirements": "Not found"
    }

    # Date extraction
    date_pattern = (
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{4}\b"
        r"|\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    )

    date_match = re.search(
        date_pattern, text, re.IGNORECASE
    )

    if date_match:
        info["Date"] = date_match.group(0)

    # Time extraction
    time_pattern = (
        r"\b(?:0?[1-9]|1[0-2])"
        r"(?::[0-5]\d)?\s*(?:AM|PM)\b"
    )

    time_match = re.search(
        time_pattern, text, re.IGNORECASE
    )

    if time_match:
        info["Time"] = time_match.group(0)

    # Venue extraction
    venue_pattern = (
        r"\b(?:Computer|Programming|AI|Cloud|NLP|"
        r"Data Science|Cyber|Innovation|Project)\s+"
        r"Lab(?:oratory)?(?:\s*(?:No\.?\s*)?\d+)?\b"
        r"|\b(?:Seminar Hall|Main Auditorium|Auditorium|"
        r"Examination Hall|Research Hall|Exhibition Hall|"
        r"College Sports Ground|Library|Conference Room)"
        r"(?:\s*(?:No\.?\s*)?\d+)?\b"
        r"|\bRoom\s*(?:No\.?\s*)?\d+\b"
        r"|\bBlock\s+[A-Z]\s*,?\s*Room\s*\d+\b"
    )

    venue_match = re.search(
        venue_pattern, text, re.IGNORECASE
    )

    if venue_match:
        info["Venue"] = venue_match.group(0).strip()

    # Department extraction
    department_pattern = (
        r"\bDepartment of [A-Za-z& -]+"
        r"|\b[A-Za-z& -]+ Department\b"
    )

    department_match = re.search(
        department_pattern, text, re.IGNORECASE
    )

    if department_match:
        info["Department"] = department_match.group(0).strip()

    # Deadline extraction
    deadline_pattern = (
        r"\b(?:deadline|due date|last date|last day|"
        r"submission deadline|submit|submission)\b"
        r"[^.!?\n]{0,100}"
    )

    deadline_match = re.search(
        deadline_pattern, text, re.IGNORECASE
    )

    if deadline_match:
        info["Deadline"] = deadline_match.group(0).strip()

    # Requirements extraction
    requirement_pattern = (
        r"\b(?:must bring|bring|carry|must carry|"
        r"required to bring|requirements?)\b"
        r"[^.!?\n]{0,150}"
    )

    requirement_match = re.search(
        requirement_pattern, text, re.IGNORECASE
    )

    if requirement_match:
        info["Requirements"] = requirement_match.group(0).strip()

    # Event extraction
    event_pattern = (
        r"\b(?:Machine Learning|Artificial Intelligence|"
        r"Data Science|Computer Science|Blockchain|"
        r"Python|Java|Cloud Computing)?\s*"
        r"(?:practical exam|written exam|oral exam|"
        r"examination|exam|workshop|seminar|placement drive|"
        r"placement|orientation|meeting|lecture|competition|"
        r"submission|webinar|conference|festival|fest|"
        r"sports event|training session)\b"
    )

    event_match = re.search(
        event_pattern, text, re.IGNORECASE
    )

    if event_match:
        info["Event"] = event_match.group(0).strip()

    return info


# ==========================================================
# 6. NOTICE CLASSIFICATION
# ==========================================================

def classify_notice(text):
    categories = {
        "Examination": [
            "exam", "examination", "practical", "viva", "test"
        ],
        "Placement": [
            "placement", "recruitment", "interview", "job drive"
        ],
        "Workshop": [
            "workshop", "hands-on", "training session"
        ],
        "Seminar": [
            "seminar", "webinar", "guest lecture"
        ],
        "Assignment": [
            "assignment", "submission", "submit", "project report"
        ],
        "Holiday": [
            "holiday", "college will remain closed", "vacation"
        ],
        "Event": [
            "festival", "fest", "competition", "celebration",
            "sports event", "orientation", "conference"
        ]
    }

    text_lower = text.lower()

    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category

    return "General"


# ==========================================================
# 7. TEXT SUMMARIZATION
# ==========================================================

def summarize_text(text):
    doc = nlp(text)

    sentences = [
        sent.text.strip()
        for sent in doc.sents
        if sent.text.strip()
    ]

    if not sentences:
        return "No summary available."

    return " ".join(sentences[:2])


# ==========================================================
# 8. QUESTION ANSWERING
# ==========================================================

def answer_question(question, info, text, category):
    q = question.lower().strip()

    if not q:
        return "Please enter a question."

    # Venue
    if any(word in q for word in [
        "where", "venue", "location"
    ]):
        if info["Venue"] != "Not found":
            return f"The venue is {info['Venue']}."
        return "The venue was not found in the notice."

    # Deadline
    if any(word in q for word in [
        "deadline", "due date", "last date"
    ]):
        if info["Deadline"] != "Not found":
            return info["Deadline"]
        return "No deadline information was found."

    # Requirements
    if any(word in q for word in [
        "bring", "carry", "required", "requirements",
        "what do i need", "what should students"
    ]):
        if info["Requirements"] != "Not found":
            return info["Requirements"]
        return "No specific requirements were found."

    # Date and time
    if any(word in q for word in [
        "when", "date", "time", "what day"
    ]):
        date = info["Date"]
        time = info["Time"]

        if date != "Not found" and time != "Not found":
            return f"The date is {date} and the time is {time}."

        if date != "Not found":
            return f"The date is {date}."

        if time != "Not found":
            return f"The time is {time}."

        return "The date and time were not found in the notice."

    # Department
    if "department" in q:
        if info["Department"] != "Not found":
            return info["Department"]
        return "No department information was found."

    # Category
    if any(word in q for word in [
        "category", "type of notice", "classify"
    ]):
        return f"This notice is classified as: {category}."

    # Event
    if any(word in q for word in [
        "event", "activity", "program", "what is happening"
    ]):
        if info["Event"] != "Not found":
            return info["Event"]
        return f"The notice category is {category}."

    # Summary
    if any(word in q for word in [
        "summarize", "summary", "about"
    ]):
        return summarize_text(text)

    return (
        "I could not answer that question directly. "
        "Try asking about the event, date, time, venue, "
        "department, deadline, or required items."
    )


# ==========================================================
# 9. MAIN HEADER
# ==========================================================

st.markdown("# 🎓 CollegeNoticeIQ")

st.markdown(
    "<p style='color:#60718a;margin-top:0'>"
    "College Notice Understanding System · NLP Mini Project"
    "</p>",
    unsafe_allow_html=True
)


# ==========================================================
# 10. NOTICE INPUT
# ==========================================================

notice = st.text_area(
    "Paste your college notice",
    height=90,
    placeholder=(
        "Example: The Machine Learning practical exam will be held "
        "on 18 October 2026 at 10 AM in Computer Lab 2. "
        "Students must bring their journal and college ID card."
    ),
    key="notice_input"
)

if st.button("🔍 Analyze Notice", type="primary"):
    if not notice.strip():
        st.warning("Please enter a college notice first.")

    else:
        doc = nlp(notice)

        st.session_state.analysis = {
            "notice": notice.strip(),
            "info": extract_information(notice),
            "category": classify_notice(notice),
            "summary": summarize_text(notice),
            "tokens": preprocess_text(notice),
            "entities": [
                {
                    "text": ent.text,
                    "label": ent.label_
                }
                for ent in doc.ents
            ]
        }

        st.session_state.pop("notice_answer", None)


# ==========================================================
# 11. TWO-COLUMN DASHBOARD
# ==========================================================

if st.session_state.get("analysis") is not None:

    result = st.session_state.analysis

    left, right = st.columns(
        [1.1, 1],
        gap="medium"
    )

    # ------------------------------------------------------
    # LEFT COMPARTMENT: NOTICE ANALYSIS
    # ------------------------------------------------------

    with left:
        with st.container(border=True, height=440):

            st.markdown("### 📋 Notice Analysis")

            safe_category = html.escape(result["category"])

            st.markdown(
                f'<span class="category-chip">'
                f'{safe_category}</span>',
                unsafe_allow_html=True
            )

            # Extracted fields
            for field, value in result["info"].items():
                safe_field = html.escape(str(field))
                safe_value = html.escape(str(value))

                st.markdown(
                    f'<div class="info-row">'
                    f'<span class="info-label">{safe_field}</span>'
                    f'<span class="info-value">{safe_value}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("#### 📝 Notice Summary")

            safe_summary = html.escape(result["summary"])

            st.markdown(
                f'<div class="summary-box">{safe_summary}</div>',
                unsafe_allow_html=True
            )

    # ------------------------------------------------------
    # RIGHT COMPARTMENT: QUESTION ANSWERING AND NER
    # ------------------------------------------------------

    with right:
        with st.container(border=True, height=440):

            st.markdown("### 💬 Ask Questions")

            question = st.text_input(
                "Ask about the notice",
                placeholder="e.g. Where is the exam?",
                key="notice_question"
            )

            if st.button("Get Answer", key="get_answer"):
                if question.strip():
                    st.session_state.notice_answer = answer_question(
                        question,
                        result["info"],
                        result["notice"],
                        result["category"]
                    )
                else:
                    st.session_state.notice_answer = (
                        "Please enter a question."
                    )

            if st.session_state.get("notice_answer"):
                safe_answer = html.escape(
                    st.session_state.notice_answer
                )

                st.markdown(
                    f'<div class="answer-box">'
                    f'<b>Answer:</b> {safe_answer}</div>',
                    unsafe_allow_html=True
                )

            st.divider()

            st.markdown("#### 🔎 Named Entity Recognition")

            if result["entities"]:
                for entity in result["entities"]:
                    safe_entity = html.escape(entity["text"])
                    safe_label = html.escape(entity["label"])

                    st.markdown(
                        f'<div class="info-row">'
                        f'<span class="info-value">'
                        f'{safe_entity}</span>'
                        f'<span class="info-label">'
                        f'{safe_label}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.caption("No named entities detected.")

            with st.expander("View preprocessed tokens"):
                st.write(result["tokens"])

else:
    st.info(
        "Enter a college notice and click Analyze Notice "
        "to view the dashboard."
    )


# ==========================================================
# 12. FOOTER
# ==========================================================

st.markdown(
    "<div class='footer-text'>"
    "CollegeNoticeIQ · NLP Mini Project"
    "</div>",
    unsafe_allow_html=True
)
