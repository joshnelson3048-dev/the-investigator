# the-investigator

An AI-powered security & network analyst I'm building across 8 weeks.

**Live app:** [the-investigator on Streamlit Cloud](https://the-investigator-joshnelson.streamlit.app/)

## What it does
- **Correlate & Triage** — upload multiple log files; Groq correlates them into a MITRE-mapped incident report
- **Ask the Investigator** — chat follow-ups about the current case
- **Case Files** — browse timestamped reports written by the Week 5 triage pipeline in `reports/`
- **Autonomous Investigation** — agentic mode: the model chooses tools (`list_evidence`, `read_log`, `lookup_mitre`) and produces a verdict (see `agent.py`)
- **Auto-Triage pipeline** — push new evidence to `evidence/`; GitHub Actions runs Ollama and commits a fresh report
- **Docker** — `docker build -t investigator-agent .` then `docker run --rm -e GROQ_API_KEY=... investigator-agent`

## Skills so far
- Week 1: Thinks like a security analyst (prompt library)
- Week 2: Can triage suspicious emails — check headers (SPF/DKIM/DMARC, Reply-To), flag urgency/secrecy/authority, recommend out-of-band verification.
- Week 3: Can audit server logs for failed-login and brute-force patterns (see audit.py).
- Week 4: Can hunt network beaconing (hunt.py) and reconstruct an incident timeline from multiple logs (timeline.py).
- Week 5: Runs an automated triage pipeline (GitHub Actions + a local Llama 3.2 model via Ollama) that reads the IR runbook, maps findings to MITRE ATT&CK, and writes a timestamped incident report (see triage.py).
- Week 6: A Streamlit SOC Copilot that correlates four telemetry sources (firewall, Sysmon, Windows, Suricata) via Groq and returns a triaged report with MITRE mapping, severity, and response plan (see app.py).
- Week 7: Deployed the SOC Copilot to Streamlit Cloud; Case Files tab surfaces pipeline reports from `reports/`; push-to-deploy via GitHub.
- Week 8: Autonomous agent mode (`agent.py`) — tool-calling loop with `list_evidence`, `read_log`, and `lookup_mitre`; packaged in Docker and integrated as the Autonomous Investigation tab in the live app.

More coming each week.
