# 2025-04-01: Prompt Injection Bypassed Rate Limiter

**Severity:** High  
**Impact:** ~200 abusive/manipulative requests processed in < 2 minutes  
**Affected:** All users (degraded response quality during window)

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 14:02 | First suspicious request detected by monitoring |
| 14:04 | Volume spike: 200 requests from 50 different IPs |
| 14:07 | On-call engineer alerted via PagerDuty |
| 14:12 | Rate limiter config updated (user_id + IP composite key) |
| 14:15 | Attack traffic dropped to zero |
| 14:30 | Post-incident review started |

## Root Cause

The rate limiter was keyed only on **source IP**. The attacker used **rotating residential proxies**, so each request appeared to come from a new IP and was allowed through. Additionally, the prompt injection guard was checking only exact-match patterns, missing the adversarial variation used.

## Fix

1. Changed rate limiter key from `IP` → `user_id + IP` composite.
2. Added token bucket per API key (not just per IP).
3. Extended injection pattern list with regex variants.
4. Added model-based secondary injection check (fallback to regex when no key).

## Lessons Learned

- **Never trust IP alone** for rate limiting — identities must be authenticated.
- **Defence in depth**: rate limits + injection detection + audit logs working together prevented persistent harm.
- **Alert on anomaly patterns**, not just raw request count.

## Follow-up Actions

- [ ] Integrate Cloudflare bot management at the edge
- [ ] Add honeypot endpoints to detect scanning behaviour
- [ ] Review injection patterns quarterly with a red team
