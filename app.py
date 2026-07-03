import html
import json
from pathlib import Path

import streamlit as st

DATA_FILE = Path(__file__).parent / "todos.json"
CATEGORIES = ["업무", "개인", "공부"]
FILTERS = ["전체"] + CATEGORIES
CATEGORY_COLORS = {
    "업무": ("#dbeafe", "#1d4ed8"),
    "개인": ("#dcfce7", "#15803d"),
    "공부": ("#ffedd5", "#c2410c"),
}


def load_todos():
    if not DATA_FILE.exists():
        return []
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_todos(todos):
    try:
        DATA_FILE.write_text(
            json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError as e:
        st.warning(f"할 일을 저장하지 못했습니다: {e}")


def init_state():
    if "todos" not in st.session_state:
        st.session_state.todos = load_todos()
    if "current_filter" not in st.session_state:
        st.session_state.current_filter = "전체"


def next_id():
    ids = [t["id"] for t in st.session_state.todos]
    return max(ids) + 1 if ids else 1


def add_todo(text, category):
    text = text.strip()
    if not text:
        return
    st.session_state.todos.append(
        {"id": next_id(), "text": text, "category": category, "completed": False}
    )
    save_todos(st.session_state.todos)


def toggle_todo(todo_id):
    for t in st.session_state.todos:
        if t["id"] == todo_id:
            t["completed"] = not t["completed"]
            break
    save_todos(st.session_state.todos)


def delete_todo(todo_id):
    st.session_state.todos = [t for t in st.session_state.todos if t["id"] != todo_id]
    save_todos(st.session_state.todos)


def get_filtered_todos():
    if st.session_state.current_filter == "전체":
        return st.session_state.todos
    return [t for t in st.session_state.todos if t["category"] == st.session_state.current_filter]


st.set_page_config(page_title="할 일 관리", page_icon="✅", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background-color: #f4f5f7; }
    .block-container {
        max-width: 480px;
        margin: 0 auto;
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, #6dd5c0, #4f9dff);
        transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[role="radiogroup"] { gap: 6px; flex-wrap: wrap; }
    div[role="radiogroup"] label {
        background: #f1f2f5;
        border-radius: 999px;
        padding: 4px 14px;
        margin: 0 !important;
        transition: background 0.15s ease, color 0.15s ease;
    }
    div[role="radiogroup"] label:hover { background: #e6e8ec; }
    div[role="radiogroup"] label:has(input:checked) { background: #2b2d33; color: #fff; }
    .stButton > button {
        border-radius: 10px;
        transition: background 0.15s ease, color 0.15s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()

st.markdown("<h1 style='text-align:center;'>할 일 관리</h1>", unsafe_allow_html=True)

with st.form("add_form", clear_on_submit=True):
    col_input, col_category, col_add = st.columns([3, 1, 1])
    with col_input:
        text_input = st.text_input(
            "할 일", placeholder="할 일을 입력하세요", label_visibility="collapsed"
        )
    with col_category:
        category_input = st.selectbox(
            "카테고리", CATEGORIES, index=1, label_visibility="collapsed"
        )
    with col_add:
        submitted = st.form_submit_button("추가", use_container_width=True)

    if submitted:
        add_todo(text_input, category_input)

# 프로그레스 바 영역을 먼저 예약해두고, 아래 필터 탭에서 선택된 값을 반영해 나중에 채워 넣는다.
progress_area = st.container()

st.radio(
    "필터",
    FILTERS,
    horizontal=True,
    label_visibility="collapsed",
    key="current_filter",
)

filtered_todos = get_filtered_todos()
total = len(filtered_todos)
done = sum(1 for t in filtered_todos if t["completed"])
percent = round((done / total) * 100) if total else 0

with progress_area:
    st.progress(percent / 100)
    st.markdown(
        f"<div style='text-align:right;color:#888;font-size:13px;margin-top:4px;'>{percent}%</div>",
        unsafe_allow_html=True,
    )

if not filtered_todos:
    st.caption("표시할 할 일이 없습니다.")

for todo in filtered_todos:
    col_check, col_text, col_tag, col_delete = st.columns([0.08, 0.6, 0.2, 0.12])

    with col_check:
        st.checkbox(
            "완료 여부",
            value=todo["completed"],
            key=f"chk_{todo['id']}",
            on_change=toggle_todo,
            args=(todo["id"],),
            label_visibility="collapsed",
        )

    with col_text:
        style = "text-decoration:line-through;color:#b0b3b8;" if todo["completed"] else ""
        st.markdown(
            f"<span style='{style}font-size:14px;'>{html.escape(todo['text'])}</span>",
            unsafe_allow_html=True,
        )

    with col_tag:
        bg, fg = CATEGORY_COLORS.get(todo["category"], ("#eee", "#555"))
        st.markdown(
            f"<span style='background:{bg};color:{fg};font-size:11px;font-weight:600;"
            f"padding:3px 9px;border-radius:999px;white-space:nowrap;'>"
            f"{html.escape(todo['category'])}</span>",
            unsafe_allow_html=True,
        )

    with col_delete:
        st.button(
            "삭제",
            key=f"del_{todo['id']}",
            on_click=delete_todo,
            args=(todo["id"],),
            use_container_width=True,
        )
