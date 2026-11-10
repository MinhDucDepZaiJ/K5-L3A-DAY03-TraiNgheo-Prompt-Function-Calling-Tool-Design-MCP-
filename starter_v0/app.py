from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from chat import ARTIFACTS_DIR, run_model_tool_loop, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
SAMPLE_QUESTIONS = [
    "Tìm 3 paper arXiv mới nhất về tool calling cho LLM agent và tóm tắt ngắn.",
    "Công ty có chính sách gì về việc đăng bài ra bên ngoài?",
    "Tìm trên web tin mới về Model Context Protocol (MCP).",
]


@st.cache_data
def load_artifacts(prompt_path: str, tools_path: str):
    system_prompt = Path(prompt_path).read_text(encoding="utf-8")
    declarations = load_tool_declarations(Path(tools_path))
    return system_prompt, declarations


with st.sidebar:
    st.header("⚙️ Cài đặt")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model = st.text_input("Model (để trống = mặc định)", value="") or None
    history_window = st.slider("History window (cặp hội thoại)", 1, 10, 5)
    max_rounds = st.slider("Max tool rounds", 1, 8, 4)
    show_tools = st.checkbox("Hiện chi tiết tool call", value=True)

    system_prompt, declarations = load_artifacts(
        str(ARTIFACTS_DIR / "system_prompt.md"), str(ARTIFACTS_DIR / "tools.yaml")
    )
    names = [d["name"] for d in declarations]
    default_tools = [n for n in names if n != "send"]
    enabled = st.multiselect("Tool bật", names, default=default_tools)

    st.markdown("**Tool của agent**")
    for d in declarations:
        desc = (d.get("description") or "").strip().split("\n")[0]
        st.caption(f"`{d['name']}` — {desc[:90]}")

    if st.button("🗑️ Xoá hội thoại"):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("history", [])

st.title("🔎 Research Agent")
st.caption("Agent nghiên cứu dùng function calling. Thử câu hỏi mẫu ở dưới hoặc tự nhập.")

cols = st.columns(len(SAMPLE_QUESTIONS))
picked = None
for col, q in zip(cols, SAMPLE_QUESTIONS):
    if col.button(q, use_container_width=True):
        picked = q


def render_events(events):
    for ev in events:
        with st.expander(f"🔧 {ev['tool']}({json.dumps(ev.get('args', {}), ensure_ascii=False)[:100]})"):
            st.code(json.dumps(ev, ensure_ascii=False, indent=2, default=str)[:6000], language="json")


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if show_tools and m.get("events"):
            render_events(m["events"])

user_text = st.chat_input("Nhập câu hỏi...") or picked

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Agent đang suy nghĩ / gọi tool..."):
            try:
                provider = make_provider(provider_name)
                tools = to_openai_tools([d for d in declarations if d["name"] in enabled])
                messages = [
                    {"role": "system", "content": system_prompt},
                    *trim_history(st.session_state.history, history_window),
                    {"role": "user", "content": user_text},
                ]
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=tools,
                    model=model,
                    max_tool_rounds=max_rounds,
                )
                answer = result["assistant_text"]
                events = result["tool_events"]
                st.session_state.history += [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": answer},
                ]
            except Exception as exc:
                answer = f"⚠️ Lỗi: `{type(exc).__name__}: {exc}`"
                events = []
        st.markdown(answer)
        if show_tools and events:
            render_events(events)

    st.session_state.messages.append({"role": "assistant", "content": answer, "events": events})
