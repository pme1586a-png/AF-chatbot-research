import os
import html
import streamlit as st
from openai import OpenAI
from modules import MODULES

st.set_page_config(
    page_title="심방세동 교육 챗봇",
    page_icon="❤️",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    max-width: 1050px;
    padding-top: 1.1rem;
    padding-bottom: 1rem;
}

/* 모든 버튼 왼쪽 정렬 */
div.stButton > button {
    min-height: 3.2rem;
    border-radius: 14px;
    font-weight: 650;
    text-align: left !important;
    justify-content: flex-start !important;
}
div.stButton > button p,
div[data-testid="stButton"] > button,
div[data-testid="stButton"] > button > div,
div[data-testid="stButton"] > button [data-testid="stMarkdownContainer"],
div[data-testid="stButton"] > button [data-testid="stMarkdownContainer"] p,
.stButton button,
.stButton button > div,
.stButton button p {
    text-align: left !important;
    justify-content: flex-start !important;
}
div[data-testid="stButton"] > button [data-testid="stMarkdownContainer"],
.stButton button [data-testid="stMarkdownContainer"] {
    width: 100% !important;
}
[data-testid="stSidebar"] div.stButton > button {
    font-size: 0.98rem;
}

/* 선택한 질문 바로 아래에 표시되는 교육내용 */
.education-box {
    margin: 0.15rem 0 0.85rem 0;
    padding: 1.0rem 1.05rem;
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 14px;
    background: rgba(128,128,128,0.06);
}
.education-label {
    font-size: 1rem;
    font-weight: 750;
    margin-bottom: 0.45rem;
}
.education-answer {
    font-size: 1.08rem;
    line-height: 1.85;
}
.education-source {
    margin-top: 0.85rem;
    font-size: 0.84rem;
    line-height: 1.55;
    opacity: 0.72;
}
.hospital {
    padding: 14px 16px;
    border: 1px solid #ddd;
    border-radius: 14px;
    margin-top: 14px;
}
</style>
""", unsafe_allow_html=True)

st.title("❤️ 심방세동 교육 챗봇")
st.caption("심방세동 환자를 위한 교육용 챗봇 · 8개 교육 주제 + 추가 자유질문")

if "module" not in st.session_state:
    st.session_state.module = None
if "question" not in st.session_state:
    st.session_state.question = None
if "chat" not in st.session_state:
    st.session_state.chat = []


def get_client():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return OpenAI(api_key=key) if key else None


def select_module(mid):
    st.session_state.module = mid
    st.session_state.question = None
    st.session_state.chat = []


def select_question(i):
    st.session_state.question = i
    # 다른 고정 교육 질문으로 이동하면 이전 자유질문 대화는 초기화
    st.session_state.chat = []


def go_home():
    st.session_state.module = None
    st.session_state.question = None
    st.session_state.chat = []


def show_fixed_answer(mid, m, i, q, a):
    """선택한 질문의 바로 아래에 고정 교육내용을 표시."""
    answer_html = html.escape(a).replace("\n", "<br>")
    source_html = html.escape(m["source"])

    st.markdown(
        f"""
        <div class="education-box">
            <div class="education-label">📖 교육 내용</div>
            <div class="education-answer">{answer_html}</div>
            <div class="education-source">근거: {source_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 교육 주제 1의 첫 질문: 심전도 예시 링크
    if mid == "1" and i == 0:
        st.warning(
            "🖼️ 정상 심전도와 심방세동(AF) 심전도 비교 그림은 "
            "대한부정맥학회 공식 환자교육 자료를 확인하도록 안내합니다."
        )
        st.link_button(
            "대한부정맥학회 심전도 예시 보기",
            "https://www.k-hrs.org/general/know/diagnosis"
        )


with st.sidebar:
    if st.button("🏠 첫 화면으로", key="go_home", use_container_width=True):
        go_home()
        st.rerun()

    st.header("교육 주제")
    for mid, m in MODULES.items():
        if st.button(
            f"{m['icon']} {mid}. {m['name']}",
            key=f"m{mid}",
            use_container_width=True
        ):
            select_module(mid)
            st.rerun()

    st.divider()
    st.markdown("**☎ 병원 이용 안내**")
    st.markdown(
        "전화예약센터 **1688-6114**  \n"
        "응급실 안내 **031-219-7777**"
    )
    st.caption("응급상황은 119 또는 가까운 응급실을 우선 이용하세요.")


if st.session_state.module is None:
    st.subheader("원하는 교육 주제를 선택하세요")

    cols = st.columns(2)
    for idx, (mid, m) in enumerate(MODULES.items()):
        with cols[idx % 2]:
            if st.button(
                f"{m['icon']}  {mid}. {m['name']}",
                key=f"home{mid}",
                use_container_width=True
            ):
                select_module(mid)
                st.rerun()

    st.info(
        "교육내용은 대한부정맥학회 2024 심방세동 진료지침, "
        "2024 ESC, 2023 ACC/AHA/ACCP/HRS 지침을 중심으로 구성했습니다."
    )

    st.divider()
    st.subheader("💬 추가로 궁금한 내용을 자유롭게 질문해 주세요")
    st.caption("개인 진단·처방·약물 용량 변경·시술 결정은 제공하지 않습니다.")

    client = get_client()
    home_q_col, home_send_col = st.columns([0.86, 0.14], gap="small")

    with home_q_col:
        user = st.text_input(
            "자유질문",
            placeholder="예: 심방세동은 왜 생기나요?",
            key="home_chat_input",
            label_visibility="collapsed"
        )

    with home_send_col:
        home_send = st.button(
            "질문하기",
            key="home_send",
            use_container_width=True
        )

    if home_send and user.strip():
        st.session_state.chat.append(("user", user))

        if client:
            all_fixed = "\n\n".join(
                [
                    f"[{m2['name']}]\n"
                    + "\n".join(
                        [f"Q: {q}\nA: {a}" for q, a in m2["questions"]]
                    )
                    for m2 in MODULES.values()
                ]
            )

            system = f"""당신은 심방세동 환자 교육 챗봇이다.
아래 고정 교육내용과 대한부정맥학회 2024 심방세동 진료지침,
2024 ESC AF guideline, 2023 ACC/AHA/ACCP/HRS AF guideline 범위에서만
쉽고 간결한 한국어로 답한다.
진단, 처방, 약물 시작/중단/용량 변경, 개인별 시술 결정을 하지 않는다.
근거가 부족하면 담당 의료진에게 문의하도록 한다.
응급 의심 시 119/응급실을 우선 안내한다.
아주대학교병원 전화예약센터 1688-6114, 응급실 안내 031-219-7777.
냉각풍선 절제술은 이 연구 교육내용에서 다루지 않는다.

[고정 교육내용]
{all_fixed}"""

            try:
                r = client.responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                    input=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ]
                )
                ans = (
                    (r.output_text or "").strip()
                    or "답변을 생성하지 못했습니다. 담당 의료진에게 문의해 주세요."
                )
            except Exception:
                ans = (
                    "현재 추가 질문 답변을 불러오지 못했습니다. "
                    "교육 주제의 고정 교육내용을 참고하거나 담당 의료진에게 문의해 주세요."
                )
        else:
            ans = (
                "현재 OPENAI_API_KEY가 설정되지 않아 자유질문 AI 답변은 사용할 수 없습니다. "
                "교육 주제의 고정 교육내용은 정상적으로 이용할 수 있습니다."
            )

        st.session_state.chat.append(("assistant", ans))
        st.rerun()

    for role, text_chat in st.session_state.chat[-8:]:
        with st.chat_message(role):
            st.markdown(text_chat)

else:
    mid = st.session_state.module
    m = MODULES[mid]

    # 사용자가 요청한 한글 '이전' 버튼
    if st.button("이전", key=f"back_{mid}"):
        go_home()
        st.rerun()

    st.header(f"{m['icon']} {mid}. {m['name']}")
    st.write("궁금한 질문을 누르면 **선택한 질문 바로 아래에 교육내용이 표시됩니다.**")

    st.subheader("📋 교육 질문")

    # 핵심 변경:
    # 질문 전체 목록 뒤에 답변을 몰아서 표시하지 않고,
    # 선택한 질문의 바로 다음 위치에 답변을 삽입한다.
    for i, (q, a) in enumerate(m["questions"]):
        if st.button(
            q,
            key=f"q{mid}_{i}",
            use_container_width=True
        ):
            select_question(i)
            st.rerun()

        if st.session_state.question == i:
            show_fixed_answer(mid, m, i, q, a)

    st.divider()
    st.subheader("💬 추가로 궁금한 내용을 자유롭게 질문해 주세요")
    st.caption("개인 진단·처방·약물 용량 변경·시술 결정은 제공하지 않습니다.")

    client = get_client()
    module_q_col, module_send_col = st.columns([0.86, 0.14], gap="small")

    with module_q_col:
        user = st.text_input(
            "자유질문",
            placeholder="예: 시술 후에도 항응고제를 계속 먹어야 하나요?",
            key=f"module_chat_input_{mid}_{st.session_state.question}",
            label_visibility="collapsed"
        )

    with module_send_col:
        module_send = st.button(
            "질문하기",
            key=f"module_send_{mid}_{st.session_state.question}",
            use_container_width=True
        )

    if module_send and user.strip():
        st.session_state.chat.append(("user", user))

        if client:
            fixed = "\n\n".join(
                [f"Q: {q}\nA: {a}" for q, a in m["questions"]]
            )

            system = f"""당신은 심방세동 환자 교육 챗봇이다.
현재 교육 주제는 '{m['name']}'이다.
아래 고정 교육내용과 대한부정맥학회 2024 심방세동 진료지침,
2024 ESC AF guideline, 2023 ACC/AHA/ACCP/HRS AF guideline 범위에서만
쉽고 간결한 한국어로 답한다.
진단, 처방, 약물 시작/중단/용량 변경, 개인별 시술 결정을 하지 않는다.
근거가 부족하면 담당 의료진에게 문의하도록 한다.
응급 의심 시 119/응급실을 우선 안내한다.
아주대학교병원 전화예약센터 1688-6114, 응급실 안내 031-219-7777.
냉각풍선 절제술은 이 연구 교육내용에서 다루지 않는다.

[고정 교육내용]
{fixed}"""

            try:
                r = client.responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                    input=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ]
                )
                ans = (
                    (r.output_text or "").strip()
                    or "답변을 생성하지 못했습니다. 담당 의료진에게 문의해 주세요."
                )
            except Exception:
                ans = (
                    "현재 추가 질문 답변을 불러오지 못했습니다. "
                    "고정 교육내용을 참고하거나 담당 의료진에게 문의해 주세요."
                )
        else:
            ans = (
                "현재 OPENAI_API_KEY가 설정되지 않아 자유질문 AI 답변은 사용할 수 없습니다. "
                "위의 고정 교육내용은 정상적으로 이용할 수 있습니다."
            )

        st.session_state.chat.append(("assistant", ans))
        st.rerun()

    for role, text_chat in st.session_state.chat[-8:]:
        with st.chat_message(role):
            st.markdown(text_chat)


st.markdown(
    """<div class='hospital'>
    <b>☎ 아주대학교병원 이용 안내</b><br>
    전화예약센터 <b>1688-6114</b> &nbsp; | &nbsp; 응급실 안내 <b>031-219-7777</b><br>
    <small>갑작스러운 마비·말 어눌함, 심한 흉통·호흡곤란, 실신·의식변화,
    멈추지 않는 심한 출혈 등 응급상황은 챗봇 답변을 기다리지 말고
    119 또는 가까운 응급실을 이용하세요.</small>
    </div>""",
    unsafe_allow_html=True
)

with st.expander("📚 교육내용 근거"):
    st.markdown(
        "- 2024 대한부정맥학회 심방세동 일반 치료 진료지침\n"
        "- 2024 대한부정맥학회 심방세동 시술적 치료 진료지침\n"
        "- 2024 대한부정맥학회 심방세동 NOAC 치료 진료지침\n"
        "- 2024 ESC Guidelines for the management of atrial fibrillation\n"
        "- 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation"
    )
