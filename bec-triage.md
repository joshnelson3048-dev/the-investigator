# BEC Triage — Meridian Group wire-transfer email

## Verdict

Spoofed (impersonation). Confidence: high.

### Reasoning

* **Total Authentication Failure:** The message failed SPF, DKIM, and DMARC checks, proving the sending server has no authorization to use the `meridiangroup.com` domain.
* **Infrastructure Mismatch:** If the account were compromised, the email would originate from Meridian's authorized corporate mail servers. Instead, an external actor used an unauthorized IP to relay a forged header through Gmail's public SMTP servers.
* **Conversation Hijacking:** The attacker split the headers—using the real CEO email in the `From` field to look legitimate, but embedding a malicious external address in the `Reply-To` field to steal the response traffic.

---

## Red flags found

* Reply-To is a Gmail address, not the company domain (`mwebb.ceo2026@gmail.com` vs `marcus.webb@meridiangroup.com`)
* SPF softfail, DKIM fail, DMARC fail — sender not authorized
* Originating IP (41.223.57.188) is an African ISP, not Singapore
* Urgency (5 PM deadline), secrecy ("don't tell the team"), authority (the CEO)
* Internal hop footprint shows a private/NAT'd IP (`192.168.43.7`) consistent with an unmanaged mobile hotspot rather than an enterprise network

---

## Verification checklist (before wiring money)

1. Call the CEO back on a known, trusted number (not from the email)
2. Require a second approver for any new payee or wire
3. Verify the destination banking details using an independent, pre-existing corporate directory
4. Do not reply to the email or forward it normally, as this alerts the attacker and modifies critical header strings
5. Securely export the raw email file (.eml) and send it directly to your IT Security team to block the sender across the entire organization
6. Instruct the mail admin team to upgrade the DMARC policy from `p=none` to `p=reject` to ensure these unauthorized originations are blocked automatically in the future
