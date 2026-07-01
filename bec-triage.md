You are a cybersecurity analyst specializing in email forensics.
I'll give you the raw headers from a suspicious email claiming to be
from a CEO requesting an urgent wire transfer. Tell me: (1) where the
email actually originated (country, ISP, infrastructure); (2) what the
DKIM, SPF, and DMARC failures mean; (3) what the Reply-To discrepancy
means and why an attacker uses it; (4) whether this is legitimate,
spoofed, or from a compromised account — and your confidence level.
Be specific. I need to decide in the next 30 minutes.

Received: from mail-lj1-f201.google.com (209.85.208.201)
    by mx.meridiangroup.com; Fri, 20 Mar 2026 16:31:02 -0500
Received: from [192.168.43.7] (unknown [41.223.57.188])
    by smtp.gmail.com; Fri, 20 Mar 2026 14:30:59 -0700
From:       Marcus Webb <marcus.webb@meridiangroup.com>
Reply-To:   mwebb.ceo2026@gmail.com
X-Originating-IP: 41.223.57.188
Authentication-Results: mx.meridiangroup.com;
    dkim=fail (signature did not verify)
    spf=softfail (domain of transitioning sender)
    dmarc=fail (p=none) header.from=meridiangroup.com

Here's the breakdown — and I'll flag my confidence level on each point since you're making a time-sensitive call.
1. Where this actually originated
The message did not originate from Meridian Group's mail infrastructure. Tracing the Received chain bottom-to-top (oldest to newest):

The true originating IP is 41.223.57.188, connecting to Gmail's SMTP servers. That IP block geolocates to Nigeria (it's within an Nigerian ISP range commonly seen in BEC/419-style fraud infrastructure — I'd verify the exact allocation with a lookup tool like whois or IPinfo before you cite it as fact).
The internal address [192.168.43.7] is a private/NAT'd IP — likely a mobile hotspot or local network, not helpful for geolocation but consistent with a phone or improvised setup rather than a corporate mail server.
The email was relayed through legitimate Google infrastructure (mail-lj1-f201.google.com), which is why it doesn't look "obviously" foreign at first glance — Gmail is just the delivery vehicle, not the source of trust here.

Bottom line: someone connected to Gmail from an IP address unrelated to Meridian Group and sent a message with From: marcus.webb@meridiangroup.com. That's the core of the attack.
2. What the DKIM/SPF/DMARC failures mean

DKIM = fail — the cryptographic signature didn't verify. Either there was no valid signature at all, or it was signed by a domain that isn't meridiangroup.com. This means the message's integrity/origin can't be cryptographically confirmed.
SPF = softfail — Meridian's SPF record doesn't authorize 41.223.57.188 (or Gmail's sending pool, in this configuration) to send mail as meridiangroup.com. "Softfail" is a weaker signal than "fail" (it means the domain owner said "probably not legitimate" rather than "definitely not"), but combined with DKIM failure it's meaningful.
**DMARC = fail, with p=none** — this is the critical detail. DMARC evaluated the message and it failed, **but** Meridian's DMARC policy is set to p=none`, meaning "don't do anything about failures, just report them." That's why this landed in an inbox instead of being quarantined or rejected. This is a policy misconfiguration on Meridian's side, not evidence about the attacker — but it's the reason this attack worked at all.

Takeaway: all three authentication mechanisms independently indicate this message was not authorized by meridiangroup.com's domain infrastructure.
3. The Reply-To discrepancy
From: marcus.webb@meridiangroup.com vs Reply-To: mwebb.ceo2026@gmail.com is a classic BEC (Business Email Compromise) tell.
Why attackers do this: the From field is what the victim sees at a glance and what builds trust ("this is from my CEO"). But when the victim hits "Reply," the response routes to the attacker's actual inbox (a free Gmail account they control), not to the real Marcus Webb. This lets the attacker:

Carry on a convincing back-and-forth conversation
Avoid the real CEO ever seeing the exchange
Do this without needing to actually compromise Meridian's mail servers

This detail alone is close to disqualifying for legitimacy — there's essentially no legitimate business reason for a CEO's urgent wire request to reply to a personal Gmail address with "ceo2026" in the name.
4. Verdict
This is spoofed, not a compromised account.

If Marcus Webb's real account were compromised, the mail would originate from Meridian's actual mail servers/IP ranges and would likely pass SPF/DKIM/DMARC (since it'd be sent through legitimate infrastructure).
Instead, someone is forging the From header while using Gmail as a relay, with no valid authentication and a reply-path to a lookalike personal address.

Confidence: high that this is fraudulent (spoofed sender, classic BEC pattern — urgency, executive impersonation, wire transfer, authentication failures, mismatched reply-to). I'm not certifying the IP's exact geolocation or ISP without a live lookup — treat that detail as directional, not confirmed.
What to do in your 30 minutes

Do not reply to the email or the wire request. Don't use any contact info contained in it.
Verify out-of-band — call Marcus Webb on a known phone number (not one from this email) or walk over/Slack him directly.
Do not process the wire transfer until verified by a second channel.
Loop in your security lead / IT now — this has the hallmarks of an active BEC attempt and others in the org may be targeted too.
Preserve the original email with full headers (don't forward-as-text, which can strip headers) for IR/reporting.
