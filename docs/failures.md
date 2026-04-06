# Post-Mortems

## 2025-04-01: Prompt injection bypassed rate limiter
**Impact:** 200 abusive requests in 2 min
**Root cause:** Rate limiter keyed only on IP, attacker used rotating proxies
**Fix:** Added user_id + IP composite key, plus token bucket per API key
**Lesson:** Never trust IP alone.
