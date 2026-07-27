import os
import streamlit as st
from groq import Groq

REPORTS_DIR = "reports"

CORRELATION_SYSTEM_PROMPT = """You are a senior SOC analyst. The user will provide multiple log files
from the same incident. Correlate them into ONE story — shared hosts, IPs, accounts, and timestamps.

Return a Markdown report with exactly these five sections:

## 1. Threat Analysis
Summarize what happened, patient zero, attacker infrastructure, and impact.

## 2. MITRE ATT&CK Mapping
Table with columns: Finding | Tactic | Technique Name | Technique ID.
Only cite real MITRE technique IDs. Do not invent IDs.

## 3. Severity
Assign Low / Medium / High / Critical with one paragraph justification tied to specific evidence.

## 4. Investigation Plan
Numbered next steps for the SOC to validate and expand the investigation.

## 5. Response Plan
Numbered containment and recovery steps aligned with standard IR practice:
preserve evidence before remediation, isolate hosts (do not power off), block C2, disable
compromised accounts, restore from offline backups.

Be precise. Flag uncertainty. Only claim what the logs support."""

CHAT_SYSTEM_PROMPT = """You are The Investigator, a senior SOC analyst helping a junior analyst.
Answer questions about the uploaded logs and the correlation report below.
Recommend verifying before taking action. Never invent facts not in the evidence."""

st.set_page_config(page_title="The Investigator — SOC Copilot v1.1", layout="wide")
st.title("The Investigator — SOC Copilot v1.1")

if "analysis" not in st.session_state:
    st.session_state.analysis = ""
if "uploaded_logs" not in st.session_state:
    st.session_state.uploaded_logs = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

tab_correlate, tab_chat, tab_cases = st.tabs(
    ["Correlate & Triage", "Ask the Investigator", "Case Files"]
)


def run_correlation(all_uploaded_logs: str) -> str:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": CORRELATION_SYSTEM_PROMPT},
            {"role": "user", "content": all_uploaded_logs},
        ],
    )
    return resp.choices[0].message.content


def run_chat(user_question: str) -> str:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    context = (
        f"Uploaded logs:\n{st.session_state.uploaded_logs}\n\n"
        f"Correlation report:\n{st.session_state.analysis}"
    )
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT + "\n\n" + context}]
    for turn in st.session_state.chat_history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_question})

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
    )
    return resp.choices[0].message.content


with tab_correlate:
    st.subheader("Upload logs for correlation")
    uploaded_files = st.file_uploader(
        "Select one or more log files",
        type=["log", "txt", "md"],
        accept_multiple_files=True,
    )

    col_run, col_new = st.columns(2)
    with col_run:
        run_clicked = st.button("Run correlation", type="primary")
    with col_new:
        if st.button("Start new analysis"):
            st.session_state.analysis = ""
            st.session_state.uploaded_logs = ""
            st.session_state.chat_history = []
            st.rerun()

    if run_clicked:
        if not uploaded_files:
            st.warning("Upload at least one log file first.")
        else:
            parts = []
            for f in uploaded_files:
                content = f.read().decode("utf-8", errors="replace")
                parts.append(f"--- {f.name} ---\n{content}")
            all_uploaded_logs = "\n\n".join(parts)
            st.session_state.uploaded_logs = all_uploaded_logs

            with st.spinner("Correlating evidence..."):
                st.session_state.analysis = run_correlation(all_uploaded_logs)
            st.session_state.chat_history = []

    if st.session_state.analysis:
        st.markdown(st.session_state.analysis)
        st.download_button(
            label="Download report",
            data=st.session_state.analysis,
            file_name="incident_report.md",
            mime="text/markdown",
        )

with tab_chat:
    st.subheader("Ask about the current case")
    if not st.session_state.analysis:
        st.info("Run a correlation first, then ask follow-up questions here.")
    else:
        for turn in st.session_state.chat_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])

        question = st.chat_input("Ask the Investigator...")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                answer = run_chat(question)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()

with tab_cases:
    st.subheader("Pipeline reports")
    if os.path.isdir(REPORTS_DIR):
        md_files = sorted(
            (f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")),
            reverse=True,
        )
    else:
        md_files = []

    if not md_files:
        st.info("No case files yet. Reports saved to reports/ will appear here.")
    else:
        choice = st.selectbox("Pick a case file", md_files)
        with open(os.path.join(REPORTS_DIR, choice), encoding="utf-8") as f:
            st.markdown(f.read())
