# Ransomware Incident Response Runbook

Concise checklist mapped to **NIST SP 800-61 Rev. 2** phases. Use this as ground truth when triaging evidence and grading automated reports.

---

## 1. Preparation

- [ ] 1.1 Maintain an up-to-date asset inventory (hosts, accounts, critical data stores).
- [ ] 1.2 Maintain offline, encrypted, tested backups separate from production networks.
- [ ] 1.3 Document IR contacts, escalation paths, and communication templates.
- [ ] 1.4 Enable centralized logging (auth, endpoint, network, file activity) with adequate retention.
- [ ] 1.5 Pre-stage forensic tools and evidence-collection procedures for analysts.

---

## 2. Detection & Analysis

- [ ] 2.1 Validate the alert — confirm ransomware indicators (`.locked` extensions, ransom notes, mass file renames).
- [ ] 2.2 **Preserve evidence first** — collect and protect logs, disk images, memory captures, and network captures **before** any remediation that could overwrite or destroy them.
- [ ] 2.3 Identify scope — list affected hosts, accounts, shares, and data stores.
- [ ] 2.4 Build a timeline — correlate auth, network, and file events to establish initial access, dwell time, and impact.
- [ ] 2.5 Identify attacker infrastructure (IPs, domains, C2 endpoints) from available logs.
- [ ] 2.6 Map observed behaviors to MITRE ATT&CK tactics and techniques.
- [ ] 2.7 Determine patient zero and the attack path (e.g., brute-force login → beaconing → encryption).
- [ ] 2.8 Document findings, assumptions, and evidence gaps.

---

## 3. Containment, Eradication & Recovery

- [ ] 3.1 **Isolate affected hosts** — disconnect from the network (disable NIC / VLAN quarantine). **Do not power off** unless required; powering off can destroy volatile evidence in memory.
- [ ] 3.2 Block malicious IPs, domains, and C2 destinations at the firewall and proxy.
- [ ] 3.3 Disable or reset compromised accounts and rotate exposed credentials.
- [ ] 3.4 Preserve additional evidence from isolated systems (memory, running processes, registry) before wiping or reimaging.
- [ ] 3.5 Eradicate malware — reimage compromised hosts or remove persistence mechanisms; verify clean baselines.
- [ ] 3.6 **Restore data from known-good offline backups** — verify backup integrity and age before restore; do not pay ransom as first response.
- [ ] 3.7 Validate restored systems and monitor for re-infection before returning to production.

---

## 4. Post-Incident Activity

- [ ] 4.1 Conduct a lessons-learned review within five business days of recovery.
- [ ] 4.2 Update detection rules, runbooks, and backup/recovery procedures based on findings.
- [ ] 4.3 Report to leadership, legal, and regulators as required.
- [ ] 4.4 Retain evidence and incident records per retention policy.
- [ ] 4.5 Track remediation tasks to closure (patching, MFA enforcement, segmentation improvements).

---

## Critical ordering reminders

1. **Preserve evidence before remediation** — logs and volatile data must be collected before reimaging or cleanup.
2. **Isolate, don't power off** — network isolation preserves memory for forensic analysis.
3. **Restore from offline backups** — never trust production-attached backups during active ransomware.
