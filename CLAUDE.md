# DreamCompanyScraper — Dev Notes

## Sort logic (DO NOT CHANGE without explicit instruction)

### "For You" sort
Sort order: **date descending (newest first), then score descending, then A-Z tiebreak.**

```javascript
if (state.sort === 'foryou') return [...arr].sort((a,b) => {
  const ta = parseDate(a.posted_date) || parseDate(a.first_seen);
  const tb = parseDate(b.posted_date) || parseDate(b.first_seen);
  return tb - ta || scoreJob(b) - scoreJob(a) || a.title.localeCompare(b.title);
});
```

Do not make this score-primary. The intent is: surface the freshest jobs first, use score to break ties within the same day/date bucket.

### parseDate
Future dates (e.g. Tesla's `pu` expiration field) return 0 so they don't float to top of Newest or For You:
```javascript
return d.getTime() > Date.now() ? 0 : d.getTime();
```
Do not remove this cap.


