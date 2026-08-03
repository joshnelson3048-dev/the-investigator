# The Investigator

**An AI-assisted SOC copilot that turns messy logs into an investigation you can verify.**

Upload telemetry, correlate incidents across sources, browse reports your pipeline wrote overnight, let an autonomous agent hunt through evidence, or ask for five practical troubleshooting steps — all behind one Streamlit app.

| | |
|---|---|
| **Live app** | [the-investigator-joshnelson.streamlit.app](https://the-investigator-joshnelson.streamlit.app/) |
| **Docker image** | [hub.docker.com/r/joshnelson3048/investigator-agent](https://hub.docker.com/r/joshnelson3048/investigator-agent) |
| **Repo** | [github.com/joshnelson3048-dev/the-investigator](https://github.com/joshnelson3048-dev/the-investigator) |

> **Important:** This tool drafts analysis. A human still has to check MITRE IDs, timelines, and recommended actions against the raw logs before anything is treated as truth.

---

## What you can do in the app

The live product has five tabs:

1. **Correlate & Triage** — Upload one or more log files. Groq correlates them into a Markdown incident report (threat analysis, MITRE ATT&CK mapping, severity, investigation plan, response plan).
2. **Ask the Investigator** — Chat about the case you just correlated (patient zero, accounts, next checks).
3. **Case Files** — Browse timestamped reports from the automated triage pipeline in `reports/` (no AI call — just display).
4. **Autonomous Investigation** — Runs the same tool-calling agent as `agent.py`: it chooses `list_evidence`, `read_log`, and `lookup_mitre`, then prints a verdict. Supervise the tool trail.
5. **Troubleshoot** — Describe an IT/network problem; get five numbered first steps to try (formatted in code so numbering is reliable).

---

## How it works

```text
                    ┌─────────────────────────────┐
   You upload logs  │  Streamlit app (app.py)     │  Groq API
   or ask a Q  ───► │  Correlate / Chat / Agent   │◄──────────►
                    │  Troubleshoot               │  llama-3.3-70b
                    └──────────────┬──────────────┘
                                   │ reads
                                   ▼
                    ┌─────────────────────────────┐
   git push to      │  evidence/   (incoming logs)│
   evidence/** ───► │  GitHub Actions + Ollama    │
                    │  triage.py → reports/*.md   │
                    └─────────────────────────────┘
                                   │
                                   ▼ Case Files tab
```

### Three modes, one product

| Mode | Who drives? | Engine | Output |
|------|-------------|--------|--------|
| **Interactive** | You upload / ask | Groq via Streamlit | Correlation report + chat |
| **Pipeline** | New files in `evidence/` | GitHub Actions + Ollama (`llama3.2:3b`) | Timestamped report in `reports/` |
| **Autonomous agent** | The model picks tools | Groq tool-calling loop (`agent.py`) | Tool trail + verdict (CLI, Docker, or app tab) |

### The agent loop (in one sentence)

Tell the model a goal and the tools it may use → it either calls a tool or returns a final answer → your code runs the tool and feeds the result back → repeat until it stops (bounded by `max_steps`).

Tools available to the agent:

- `list_evidence()` — filenames in `evidence/`
- `read_log(filename)` — contents of one log
- `lookup_mitre(technique_id)` — verify ATT&CK IDs before citing them

### Secrets

- Locally: `.streamlit/secrets.toml` with `GROQ_API_KEY = "..."` (gitignored)
- Streamlit Cloud: same key in **Settings → Secrets**
- Docker / CLI: pass `-e GROQ_API_KEY=...` at run time — **never bake the key into the image or commit it**

---

## Quick start

### Run the web app locally

```bash
pip install -r requirements.txt
# Create .streamlit/secrets.toml with: GROQ_API_KEY = "gsk_..."
python -m streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

### Run the autonomous agent (CLI)

```bash
# Key from environment, or from .streamlit/secrets.toml
python agent.py
```

### Run the agent in Docker

```bash
docker pull joshnelson3048/investigator-agent:1.0
docker run --rm -e GROQ_API_KEY="your_key" joshnelson3048/investigator-agent:1.0
```

Or build from this repo:

```bash
docker build -t investigator-agent .
docker run --rm -e GROQ_API_KEY="your_key" investigator-agent
```

### Trigger the auto-triage pipeline

1. Add or update a log under `evidence/`
2. Commit and push to `main`
3. Watch **Actions → Auto-Triage** (installs Ollama, runs `triage.py`, commits a new `reports/report_YYYY-MM-DD_HHMM.md`)
4. `git pull` locally; the Case Files tab shows the new report after Streamlit redeploys

---

## Project layout

```text
the-investigator/
├── app.py                      # Streamlit SOC Copilot (all tabs)
├── agent.py                    # Autonomous tool-calling agent
├── triage.py                   # CI triage: evidence + runbook → report
├── ir_runbook.md               # NIST 800-61 ransomware IR checklist
├── investigator-instructions.md
├── requirements.txt            # streamlit, groq, rich
├── Dockerfile                  # Packages agent + evidence/
├── evidence/                   # Logs the pipeline & agent read
├── reports/                    # Timestamped incident reports
├── samples/                    # Multi-source case (firewall, Sysmon, …)
├── audit.py / hunt.py / timeline.py   # Earlier analysis scripts
└── .github/workflows/triage.yml
```

### Sample evidence

| Folder | Contents |
|--------|----------|
| `evidence/` | Auth, network, file, and security-event logs for automated triage / agent |
| `samples/` | Four-source intrusion set (firewall, Sysmon, Windows Event, Suricata) for Correlate & Triage practice |

---

## Demo checklist

1. Open the [live app](https://the-investigator-joshnelson.streamlit.app/)
2. **Correlate & Triage** — upload the four files from `samples/`
3. **Ask the Investigator** — e.g. “Which host is patient zero?”
4. **Case Files** — open a pipeline report from `reports/`
5. **Autonomous Investigation** — run and watch the tool trail
6. **Troubleshoot** — e.g. “I can’t ping anything” → five numbered steps

Optional: `python agent.py` or the Docker `run` above for a CLI/container demo of the same agent.

---

## Design principles

- **Verify, don’t trust** — AI drafts; humans check IDs, scope, and actions
- **Evidence in → report out** — `evidence/` and `reports/` stay separate so report commits don’t re-trigger the pipeline
- **Keys stay out of git** — `git ls-files | grep -i secret` should return nothing
- **Agents can read; humans approve action** — no auto-isolate / auto-block / auto-restore

---

## Built over eight weeks + final project

| Stage | Capability |
|-------|------------|
| Weeks 1–2 | Analyst voice, phishing / BEC triage |
| Weeks 3–4 | Log audit, beacon hunting, multi-log timelines |
| Week 5 | Auto-triage pipeline (Actions + Ollama + IR runbook) |
| Weeks 6–7 | Streamlit SOC Copilot on Streamlit Cloud + Case Files |
| Week 8 | Autonomous agent + Docker |
| **Final project** | Troubleshoot tab (five numbered first steps) |

---

## Stack

- **Python 3.12+**
- **Streamlit** — web UI
- **Groq** (`llama-3.3-70b-versatile`) — interactive chat, correlation, agent
- **Ollama** (`llama3.2:3b`) — CI triage job
- **GitHub Actions** — evidence-triggered pipeline
- **Docker** — portable agent image

---

## License / classroom note

Built for *Application of Generative AI in Cybersecurity & IT* (UW-Stout). Sample logs are fictional lab data — not production customer evidence.
