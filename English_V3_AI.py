import streamlit as st
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ============================================================
# English Learning Platform V2
# ============================================================

st.set_page_config(
    page_title="English Learning Platform",
    page_icon="🇬🇧",
    layout="wide",
)
# =========================
# 🔐 Access Code
# =========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

access_code = st.secrets.get("ACCESS_CODE", "")

if not access_code:
    st.error("⚠️ Access code is not configured.")
    st.stop()

if not st.session_state.authenticated:
    st.title("🔐 English Learning Platform")
    st.write("Please enter your access code to continue.")

    entered_code = st.text_input(
        "Access Code",
        type="password"
    )

    if st.button("Login"):
        if entered_code.strip() == access_code:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect access code.")

    st.stop()

# -----------------------------
# Session state
# -----------------------------
defaults = {
    "level": "A1 - Beginner",
    "points": 0,
    "completed_lessons": set(),
    "quiz_scores": {},
    "streak": 1,
    "ai_messages": [],
    "ai_errors": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# Data
# -----------------------------
LEVELS = {
    "A1 - Beginner": {
        "description": "Basic words, simple sentences and everyday expressions.",
        "lessons": [
            ("A1-1", "Greetings", "Hello, Hi, Good morning, How are you?"),
            ("A1-2", "Present Simple", "I work. She works. They play football."),
            ("A1-3", "Daily Routine", "I wake up at 7 o'clock. I go to school."),
        ],
    },
    "A2 - Elementary": {
        "description": "Everyday conversations and basic grammar.",
        "lessons": [
            ("A2-1", "Past Simple", "I visited my friend yesterday."),
            ("A2-2", "Future with will", "I will study tomorrow."),
            ("A2-3", "Comparatives", "A car is faster than a bicycle."),
        ],
    },
    "B1 - Intermediate": {
        "description": "More complex grammar, vocabulary and conversations.",
        "lessons": [
            ("B1-1", "Present Perfect", "I have finished my homework."),
            ("B1-2", "First Conditional", "If it rains, I will stay home."),
            ("B1-3", "Useful Connectors", "However, therefore, although, because."),
        ],
    },
    "B2 - Upper-Intermediate": {
        "description": "Advanced vocabulary, grammar and fluent communication.",
        "lessons": [
            ("B2-1", "Passive Voice", "The book was written in 2020."),
            ("B2-2", "Reported Speech", "She said that she was tired."),
            ("B2-3", "Advanced Connectors", "Nevertheless, furthermore, whereas."),
        ],
    },
}

VOCABULARY = {
    "A1 - Beginner": [
        ("Book", "كتاب", "This is my book."),
        ("Teacher", "أستاذ", "My teacher is kind."),
        ("Student", "تلميذ", "I am a student."),
        ("School", "مدرسة", "I go to school every day."),
        ("Computer", "حاسوب", "I use a computer."),
    ],
    "A2 - Elementary": [
        ("Journey", "رحلة", "Our journey was very interesting."),
        ("Healthy", "صحي", "Fruit is healthy."),
        ("Weather", "الطقس", "The weather is nice today."),
        ("Important", "مهم", "English is important for me."),
        ("Improve", "يحسن", "I want to improve my English."),
    ],
    "B1 - Intermediate": [
        ("Opportunity", "فرصة", "This is a great opportunity."),
        ("Decision", "قرار", "It was a difficult decision."),
        ("Experience", "خبرة / تجربة", "I have work experience."),
        ("Achieve", "يحقق", "She wants to achieve her goal."),
        ("Environment", "بيئة", "We should protect the environment."),
    ],
    "B2 - Upper-Intermediate": [
        ("Nevertheless", "مع ذلك", "It was difficult; nevertheless, we continued."),
        ("Consequently", "وبالتالي", "He was late; consequently, he missed the bus."),
        ("Significant", "مهم / كبير", "There was a significant improvement."),
        ("Approach", "نهج / أسلوب", "We need a different approach."),
        ("Reliable", "موثوق", "This is a reliable source."),
    ],
}

QUIZZES = {
    "A1 - Beginner": [
        ("She ___ English every day.", ["study", "studies", "studying"], "studies"),
        ("They ___ football on Sunday.", ["play", "plays", "playing"], "play"),
        ("He ___ to school every morning.", ["go", "goes", "going"], "goes"),
    ],
    "A2 - Elementary": [
        ("Yesterday, I ___ my friend.", ["visit", "visited", "visiting"], "visited"),
        ("I think it ___ tomorrow.", ["will rain", "rained", "rains"], "will rain"),
        ("A car is ___ than a bicycle.", ["fast", "faster", "fastest"], "faster"),
    ],
    "B1 - Intermediate": [
        ("I ___ finished my homework.", ["have", "has", "having"], "have"),
        ("If it rains, I ___ at home.", ["stay", "will stay", "stayed"], "will stay"),
        ("She has lived here ___ 2020.", ["for", "since", "during"], "since"),
    ],
    "B2 - Upper-Intermediate": [
        ("The book ___ in 2020.", ["wrote", "was written", "is writing"], "was written"),
        ('He said that he ___ tired.', ["is", "was", "be"], "was"),
        ("___ it was difficult, we continued.", ["Although", "Because", "So"], "Although"),
    ],
}

# -----------------------------
# AI Tutor
# -----------------------------
def get_ai_client():
    if OpenAI is None:
        return None
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def ask_ai(message, level, history):
    client = get_ai_client()
    if client is None:
        return None, "لم يتم إعداد OPENAI_API_KEY أو مكتبة openai بعد."

    system_prompt = f"""
You are a patient English teacher inside an educational app.
Student level: {level}.

For every student message:
1. Check whether the English is correct.
2. If there is a mistake, identify the important mistake(s).
3. Give the corrected sentence.
4. Explain the reason simply in Arabic.
5. Give the Arabic meaning when useful.
6. Give one short example.
7. End with a simple practice prompt appropriate for the student's level.

When there is a mistake, use:
❌ Your sentence:
[student sentence]

✅ Correct:
[correct sentence]

📌 Explanation:
[short Arabic explanation]

🇸🇦 Meaning:
[Arabic meaning]

💡 Example:
[one simple English example]

🎯 Try:
[a short practice prompt]

If the sentence is correct, use:
✅ Correct!
[short encouragement]

📌 Note:
[one useful learning note]

🎯 Try:
[a short follow-up question]

Important:
- Do not invent mistakes.
- Keep explanations short and suitable for the student's level.
- Pay special attention to grammar, word choice, spelling, capitalization,
  articles, subject-verb agreement, and verb tenses.
- Encourage the student to practice English.
"""
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-12:])
    messages.append({"role": "user", "content": message})

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=messages,
        )
        return response.output_text, None
    except Exception as e:
        return None, f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}"


# -----------------------------
# Helpers
# -----------------------------
def add_points(amount):
    st.session_state.points += amount

def mark_lesson_done(lesson_id):
    if lesson_id not in st.session_state.completed_lessons:
        st.session_state.completed_lessons.add(lesson_id)
        add_points(10)

def progress_percent():
    total = sum(len(v["lessons"]) for v in LEVELS.values())
    done = len(st.session_state.completed_lessons)
    return done / total if total else 0

# -----------------------------
# Header
# -----------------------------
st.title("🇬🇧 English Learning Platform")
st.caption("منصة تفاعلية لتعلم الإنجليزية خطوة بخطوة")

# Sidebar
st.sidebar.title("📚 Menu")
choice = st.sidebar.radio(
    "اختر القسم:",
    [
        "🏠 Home",
        "🎯 Choose Level",
        "📖 Lessons",
        "🧠 Vocabulary",
        "📝 Exercises",
        "💬 Conversation",
        "📊 My Progress",
    ],
)

st.sidebar.divider()
st.sidebar.metric("⭐ Points", st.session_state.points)
st.sidebar.metric("🔥 Streak", f"{st.session_state.streak} day")
st.sidebar.progress(progress_percent())

# -----------------------------
# Home
# -----------------------------
if choice == "🏠 Home":
    st.header("Welcome! 👋")
    st.write("تعلم الإنجليزية من خلال الدروس والمفردات والتمارين والمحادثة.")

    c1, c2, c3 = st.columns(3)
    c1.metric("المستوى", st.session_state.level)
    c2.metric("النقاط", st.session_state.points)
    c3.metric("الدروس المكتملة", len(st.session_state.completed_lessons))

    st.divider()
    st.subheader("🚀 ماذا يمكنك أن تتعلم؟")
    st.markdown(
        """
        - 📖 Grammar & Lessons
        - 🧠 Vocabulary
        - 📝 Exercises
        - 💬 Conversation
        - 📊 متابعة التقدم
        """
    )

    st.info(
        f"🎯 مستواك الحالي: **{st.session_state.level}** — "
        f"{LEVELS[st.session_state.level]['description']}"
    )

# -----------------------------
# Choose Level
# -----------------------------
elif choice == "🎯 Choose Level":
    st.header("🎯 Choose Your English Level")

    levels = list(LEVELS.keys())
    current_index = levels.index(st.session_state.level)

    level = st.selectbox(
        "Select your level:",
        levels,
        index=current_index,
    )

    if level != st.session_state.level:
        st.session_state.level = level
        st.success(f"تم اختيار المستوى: {level}")
        st.rerun()

    st.success(f"Your selected level: **{level}**")
    st.write(LEVELS[level]["description"])

    st.subheader("محتوى هذا المستوى")
    for lesson_id, title, summary in LEVELS[level]["lessons"]:
        done = lesson_id in st.session_state.completed_lessons
        st.write(("✅ " if done else "⬜ ") + f"**{title}** — {summary}")

# -----------------------------
# Lessons
# -----------------------------
elif choice == "📖 Lessons":
    st.header("📖 Lessons")
    level = st.session_state.level

    for lesson_id, title, summary in LEVELS[level]["lessons"]:
        with st.expander(f"{'✅' if lesson_id in st.session_state.completed_lessons else '📘'} {title}"):
            st.write(summary)

            if title == "Present Simple":
                st.markdown("### القاعدة")
                st.write("نستخدم Present Simple للعادات والروتين والحقائق.")
                st.info("I go to school every day.")
                st.success("He plays football every Friday.")

            elif title == "Past Simple":
                st.markdown("### القاعدة")
                st.write("نستخدم Past Simple للحديث عن أحداث انتهت في الماضي.")
                st.info("I visited my friend yesterday.")

            elif title == "Future with will":
                st.markdown("### القاعدة")
                st.write("نستخدم will للحديث عن المستقبل والتوقعات والقرارات.")
                st.info("I will study tomorrow.")

            else:
                st.markdown("### Example")
                st.info(summary)

            if st.button("Mark lesson as completed", key=f"done_{lesson_id}"):
                mark_lesson_done(lesson_id)
                st.success("🎉 تم إكمال الدرس وحصلت على 10 نقاط!")

# -----------------------------
# Vocabulary
# -----------------------------
elif choice == "🧠 Vocabulary":
    st.header("🧠 Vocabulary")
    level = st.session_state.level

    for i, (word, meaning, example) in enumerate(VOCABULARY[level]):
        with st.container(border=True):
            col1, col2 = st.columns([1, 2])
            col1.subheader(word)
            col2.write(f"**المعنى:** {meaning}")
            col2.write(f"**Example:** {example}")

    st.info("💡 حاول كتابة جملة جديدة باستخدام كل كلمة.")

# -----------------------------
# Exercises
# -----------------------------
elif choice == "📝 Exercises":
    st.header("📝 Exercises")
    level = st.session_state.level
    questions = QUIZZES[level]

    answers = []
    for i, (question, options, correct) in enumerate(questions, start=1):
        answers.append(
            st.radio(question, options, key=f"{level}_q_{i}")
        )

    if st.button("Check my answers", type="primary"):
        score = sum(
            answer == question[2]
            for answer, question in zip(answers, questions)
        )

        previous = st.session_state.quiz_scores.get(level, 0)
        st.session_state.quiz_scores[level] = max(previous, score)

        earned = score * 5
        add_points(earned)

        st.divider()
        st.subheader("📊 Your Result")
        st.write(f"**Score: {score}/{len(questions)}**")
        st.write(f"⭐ حصلت على {earned} نقطة")

        if score == len(questions):
            st.success("🎉 Excellent! Perfect score!")
        elif score >= 2:
            st.info("👍 Good job! Keep practicing.")
        else:
            st.warning("📚 Keep practicing and try again.")

# -----------------------------
# Conversation
# -----------------------------
elif choice == "💬 Conversation":
    st.header("🤖 AI English Tutor")
    st.write(
        f"تحدث مع مدرس إنجليزي بالذكاء الاصطناعي. "
        f"المستوى الحالي: **{st.session_state.level}**"
    )

    if OpenAI is None:
        st.warning(
            "ثبت مكتبة OpenAI أولاً باستخدام: pip install openai"
        )

    if not os.getenv("OPENAI_API_KEY"):
        st.info(
            "أضف مفتاح OpenAI في متغير البيئة OPENAI_API_KEY قبل تشغيل المحادثة."
        )

    if not st.session_state.ai_messages:
        st.session_state.ai_messages.append({
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm your English tutor. "
                "Let's practice together. What is your name?"
            ),
        })

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Write your message in English...")

    if user_message:
        st.session_state.ai_messages.append({
            "role": "user",
            "content": user_message,
        })

        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, error = ask_ai(
                    user_message,
                    st.session_state.level,
                    st.session_state.ai_messages[:-1],
                )

            if error:
                st.error(error)
            else:
                st.markdown(answer)
                st.session_state.ai_messages.append({
                    "role": "assistant",
                    "content": answer,
                })

                if "❌ Your sentence:" in answer and "✅ Correct:" in answer:
                    st.session_state.ai_errors.append(
                        user_message.strip().replace("\n", " ")[:180]
                    )

                add_points(2)

    if st.button("🗑️ Clear conversation"):
        st.session_state.ai_messages = []
        st.rerun()

# -----------------------------
# Progress
# -----------------------------
elif choice == "📊 My Progress":
    st.header("📊 My Progress")

    completed = len(st.session_state.completed_lessons)
    total = sum(len(v["lessons"]) for v in LEVELS.values())

    st.metric("Total Points", st.session_state.points)
    st.metric("Completed Lessons", f"{completed}/{total}")
    st.metric("Current Level", st.session_state.level)

    st.subheader("Overall progress")
    st.progress(progress_percent())

    st.subheader("Quiz best scores")
    if st.session_state.quiz_scores:
        for level, score in st.session_state.quiz_scores.items():
            st.write(f"**{level}:** {score}/{len(QUIZZES[level])}")
    else:
        st.info("لم تكمل أي اختبار بعد.")

    st.divider()
    st.subheader("🧠 AI Learning Notes")
    if st.session_state.ai_errors:
        st.write("أمثلة من الأخطاء التي سجلتها أثناء التدريب:")
        for item in st.session_state.ai_errors[-10:]:
            st.write(f"• {item}")
    else:
        st.info("لا توجد أخطاء مسجلة بعد. ابدأ محادثة مع AI Tutor.")

    st.divider()
    st.subheader("🏆 Achievements")

    achievements = [
        ("🌱 First lesson", len(st.session_state.completed_lessons) >= 1),
        ("⭐ 50 points", st.session_state.points >= 50),
        ("🏆 100 points", st.session_state.points >= 100),
        ("📚 5 lessons", len(st.session_state.completed_lessons) >= 5),
    ]

    for name, unlocked in achievements:
        st.write(("✅ " if unlocked else "🔒 ") + name)
