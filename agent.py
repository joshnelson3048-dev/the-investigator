"""Autonomous SOC investigator — tool-calling agent loop."""

import json
import os

from groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

EVIDENCE_DIR = "evidence"
MODEL = "llama-3.3-70b-versatile"
MAX_STEPS = 12

SYSTEM = """You are The Investigator, an autonomous SOC analyst.
Investigate incidents by calling tools — never guess log contents or MITRE IDs.

Workflow:
1. list_evidence() to see available logs
2. read_log() on every relevant file before concluding
3. lookup_mitre() on every technique ID you cite in your verdict

When you have enough evidence, stop calling tools and write a Markdown verdict with:
Summary, Timeline, Root Cause, MITRE ATT&CK table (verified IDs only), and Recommended Actions.
Flag uncertainty. Never invent hosts, IPs, or events not in the logs."""

MITRE_DB = {
    "T1110": "Brute Force — credential guessing against accounts",
    "T1071": "Application Layer Protocol — C2 over HTTP/HTTPS/custom ports",
    "T1071.001": "Application Layer Protocol: Web Protocols",
    "T1486": "Data Encrypted for Impact — ransomware file encryption",
    "T1136": "Create Account — adversary creates a local/domain account",
    "T1078": "Valid Accounts — use of legitimate credentials",
    "T1059.001": "Command and Scripting Interpreter: PowerShell",
    "T1566.001": "Phishing: Spearphishing Attachment",
    "T1021": "Remote Services — lateral movement via RDP/SMB/SSH",
    "T1021.001": "Remote Services: Remote Desktop Protocol",
    "T1190": "Exploit Public-Facing Application",
}


def list_evidence() -> list[str]:
    """List log filenames in the evidence/ folder."""
    if not os.path.isdir(EVIDENCE_DIR):
        return []
    return sorted(
        f for f in os.listdir(EVIDENCE_DIR)
        if os.path.isfile(os.path.join(EVIDENCE_DIR, f))
    )


def read_log(filename: str) -> str:
    """Read one evidence log file by name."""
    path = os.path.join(EVIDENCE_DIR, filename)
    if not os.path.isfile(path):
        return f"Error: file not found: {filename}"
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def lookup_mitre(technique_id: str) -> str:
    """Look up a MITRE ATT&CK technique ID."""
    tid = technique_id.strip().upper()
    if not tid.startswith("T"):
        tid = "T" + tid
    if tid in MITRE_DB:
        return f"{tid}: {MITRE_DB[tid]}"
    return (
        f"{tid}: not in local cache — verify at "
        f"https://attack.mitre.org/techniques/{tid.replace('.', '/')}/"
    )


AVAILABLE = {
    "list_evidence": list_evidence,
    "read_log": read_log,
    "lookup_mitre": lookup_mitre,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_evidence",
            "description": "List all log filenames in the evidence/ folder.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_log",
            "description": "Read the full contents of one evidence log file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Log filename from list_evidence, e.g. auth_events.log",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_mitre",
            "description": "Verify a MITRE ATT&CK technique ID before citing it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "technique_id": {
                        "type": "string",
                        "description": "Technique ID, e.g. T1110 or T1071.001",
                    }
                },
                "required": ["technique_id"],
            },
        },
    },
]


def run_agent(
    goal: str,
    api_key: str | None = None,
    on_tool_call=None,
) -> str:
    """Run the agent loop; return the final Markdown verdict."""
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY not set in environment or argument")

    client = Groq(api_key=key)
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": goal},
    ]

    for _step in range(MAX_STEPS):
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content or ""

        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}") or {}
            result = AVAILABLE[name](**args)
            if on_tool_call:
                on_tool_call(name, args, result)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": str(result),
                }
            )

    return "Agent hit the step limit before producing a final verdict."


def _cli_main() -> None:
    console = Console()
    tree = Tree("[bold]Investigator agent[/bold]")
    step_num = 0

    def on_tool(name, args, result):
        nonlocal step_num
        step_num += 1
        preview = str(result)
        if len(preview) > 120:
            preview = preview[:120] + "…"
        tree.add(f"[cyan]Step {step_num}[/cyan] {name}({args}) -> {preview}")

    goal = (
        "Investigate the incident in evidence/ and report what happened. "
        "Read all logs, verify MITRE IDs, and produce a Markdown verdict."
    )

    with console.status("[bold green]The Investigator is working…"):
        verdict = run_agent(goal, on_tool_call=on_tool)

    console.print(tree)
    console.print(Panel(verdict, title="[bold green]Verdict[/bold green]", border_style="green"))


if __name__ == "__main__":
    _cli_main()
