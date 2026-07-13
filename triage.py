import os
import ollama
from datetime import datetime

# Step 1: Read every log file in the evidence/ folder
evidence_dir = "evidence"
evidence_text = ""
for filename in sorted(os.listdir(evidence_dir)):
    filepath = os.path.join(evidence_dir, filename)
    if os.path.isfile(filepath):
        with open(filepath, "r") as f:
            evidence_text += f"\n--- {filename} ---\n{f.read()}"

# Step 2: Read the incident-response runbook
with open("ir_runbook.md", "r") as f:
    runbook_text = f.read()

# Step 3: Send evidence and runbook to the local Llama model via Ollama
prompt_text = f"""Analyze the following incident evidence and produce a Markdown incident report.

Include these sections:
1. **Summary** — one-paragraph overview of the incident
2. **Timeline** — chronological key events across all logs
3. **Root Cause** — how the attacker gained access and what they did
4. **MITRE ATT&CK Mapping** — for each finding, list tactic, technique name, and technique ID (e.g., T1110)
5. **Runbook Compliance** — which runbook steps were completed vs. missed (cite step numbers from ir_runbook.md)
6. **Recommended Next Actions** — prioritized follow-up for the SOC

Correlate the shared attacker IP (185.220.101.47) across all three logs.

## Evidence
{evidence_text}

## Incident Response Runbook
{runbook_text}
"""

resp = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a senior SOC analyst. Map findings to MITRE ATT&CK with "
                "technique IDs and cite the runbook. Only claim what the evidence supports."
            ),
        },
        {"role": "user", "content": prompt_text},
    ],
)
report = resp.message.content

# Step 4: Write the report to a timestamped file in reports/
os.makedirs("reports", exist_ok=True)
stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
report_path = f"reports/report_{stamp}.md"
with open(report_path, "w") as f:
    f.write(report)

print(f"Report written to {report_path}")
