# PromptForge Startup & Testing Guide

**Date:** 2025-10-08
**Feature:** Parent-Child Trace Hierarchical View
**Status:** ✅ ALL CRITICAL FIXES COMPLETE - READY TO TEST

---

## 🚀 Quick Start

### 1. Apply Database Migration

```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade k7i1j2k3l4m5 -> l8j2k3l4m5n6, add trace_metadata GIN indexes
```

### 2. Start API Server

**Option A: Using Python directly**
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B: Using the main.py script**
```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
python3 app/main.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Verify API is Running

Open in browser: http://localhost:8000

**Expected Response:**
```json
{
  "name": "PromptForge API",
  "version": "2.0.0",
  "status": "operational",
  "docs": "/docs"
}
```

### 4. Check Database Indexes

```bash
psql -U promptforge -d promptforge -c "
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'traces'
AND indexname LIKE 'idx_trace_metadata%';
"
```

**Expected Output:** 4 indexes
```
idx_trace_metadata_parent_trace_id
idx_trace_metadata_source
idx_trace_metadata_jsonb_path_ops
idx_trace_metadata_keys
```

### 5. Start UI (Shell + MFEs)

**Terminal 1 - Shell:**
```bash
cd /Users/rohitiyer/datagrub/promptforge/ui-tier/shell
npm run dev
```

**Terminal 2 - Traces MFE:**
```bash
cd /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-traces
npm run dev
```

**Terminal 3 - Other MFEs (if needed):**
```bash
cd /Users/rohitiyer/datagrub/promptforge/ui-tier/mfe-playground
npm run dev
```

### 6. Access Traces Dashboard

Open in browser: http://localhost:3000/traces

**Expected Result:**
- ✅ No CORS errors
- ✅ Traces list loads successfully
- ✅ Parent traces show expand/collapse icons
- ✅ Source badges display (blue/purple/gray)
- ✅ Aggregated metrics show ∑ (sum) and Ø (average) symbols

---

## 🧪 Testing Checklist

### Backend Tests

```bash
cd /Users/rohitiyer/datagrub/promptforge/api-tier
pytest tests/test_trace_parent_child.py -v
```

**Expected:** All 5 tests passing
- ✅ test_list_traces_with_parent_child_hierarchy
- ✅ test_list_traces_with_source_filter
- ✅ test_list_traces_excludes_child_traces
- ✅ test_list_traces_standalone_trace
- ✅ test_trace_detail_shows_correct_evaluations

### API Endpoint Manual Test

```bash
# Test trace list endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/traces?page=1&page_size=20

# Test with source filter
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/traces?source_filter=Call%20Insights

# Test trace detail
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/traces/{trace_id}/detail
```

### UI Functional Tests

**Traces Dashboard:**
- [ ] Page loads without errors
- [ ] Traces table renders with data
- [ ] Parent traces show expand icon (ChevronRight)
- [ ] Click expand → icon changes to ChevronDown
- [ ] Children appear indented with stage badges
- [ ] Source badges show correct colors:
  - Blue: Call Insights
  - Purple: Playground
  - Gray: Other
- [ ] Aggregated metrics show:
  - ∑ 4,500 (sum of tokens)
  - ∑ $0.0045 (sum of cost)
  - Ø 600ms (average duration)
- [ ] Source filter dropdown works
- [ ] Click parent row → opens parent trace detail modal
- [ ] Click child row → opens child trace detail modal

### Performance Tests

**Query Performance:**
```bash
# Enable query logging
# In config.py: DATABASE_ECHO = True

# Start API server and watch logs
# Expected: 2 queries per page load (1 parent + 1 bulk children)
```

**Page Load Time:**
- [ ] Trace list loads in < 100ms (vs 400ms+ before)
- [ ] No N+1 query warnings in logs
- [ ] Database index usage confirmed in query plans

---

## 🔍 Troubleshooting

### Problem: CORS Error

**Error:**
```
Access to XMLHttpRequest at 'http://localhost:8000' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**Solution:**
1. Verify API server is running on port 8000
2. Check CORS settings in `api-tier/app/core/config.py` (should include `http://localhost:3000`)
3. Restart API server if config was changed

### Problem: "Failed to load traces"

**Possible Causes:**
1. ✅ **FIXED:** JSONB operator syntax error (`has_key()` → `.op('?')()`)
2. API server not running
3. Database connection issue
4. Missing authentication token

**Debugging:**
```bash
# Check API logs for errors
tail -f api-tier/logs/app.log

# Check if endpoint returns 200
curl -v http://localhost:8000/api/v1/traces

# Check database connection
psql -U promptforge -d promptforge -c "SELECT COUNT(*) FROM traces;"
```

### Problem: No Parent Traces Showing

**Possible Causes:**
1. All traces have `parent_trace_id` in metadata (all are children)
2. Database has no trace data

**Debugging:**
```sql
-- Check parent vs child traces
SELECT
  COUNT(*) FILTER (WHERE trace_metadata ? 'parent_trace_id') as child_count,
  COUNT(*) FILTER (WHERE NOT trace_metadata ? 'parent_trace_id' OR trace_metadata IS NULL) as parent_count
FROM traces;
```

### Problem: Children Not Showing

**Possible Causes:**
1. `parent_trace_id` mismatch in metadata
2. Children query filter issue

**Debugging:**
```sql
-- Find orphaned children
SELECT
  trace_id,
  trace_metadata->>'parent_trace_id' as parent_id
FROM traces
WHERE trace_metadata ? 'parent_trace_id'
AND trace_metadata->>'parent_trace_id' NOT IN (
  SELECT trace_id FROM traces WHERE NOT trace_metadata ? 'parent_trace_id'
);
```

### Problem: Slow Page Loads

**Check:**
1. Database indexes created?
   ```sql
   SELECT * FROM pg_indexes WHERE tablename = 'traces';
   ```
2. N+1 query pattern resolved?
   - Enable `DATABASE_ECHO = True`
   - Check logs - should see only 2 queries per page

---

## 📊 Success Metrics

### Performance Benchmarks

| Metric | Target | Acceptance |
|--------|--------|------------|
| Page Load Time | < 100ms | < 200ms |
| Total Queries | 2 queries | ≤ 3 queries |
| Database Index Usage | 100% | > 90% |
| API Response Time (p95) | < 50ms | < 100ms |

### Functional Validation

- ✅ All 5 backend tests passing
- ✅ No CORS errors in browser console
- ✅ Traces dashboard renders successfully
- ✅ Parent-child expansion works
- ✅ Source filtering works
- ✅ Aggregated metrics accurate
- ✅ Navigation to detail modals works
- ✅ No JavaScript errors in console

---

## 📋 Test Data Setup

### Create Test Parent Trace (Call Insights)

```sql
-- Insert parent trace
INSERT INTO traces (
  id, trace_id, name, status, project_id,
  trace_metadata, total_tokens, total_cost, created_at
) VALUES (
  gen_random_uuid(),
  'parent-trace-001',
  'call_insights',
  'success',
  (SELECT id FROM projects LIMIT 1),
  '{"source": "Call Insights", "stage_count": 3}',
  0,
  0.0,
  NOW()
);

-- Insert 3 child traces
INSERT INTO traces (
  id, trace_id, name, status, project_id, model_name,
  trace_metadata, total_tokens, total_cost, total_duration_ms, created_at
) VALUES
(
  gen_random_uuid(),
  'child-trace-001',
  'call_insights_stage_1',
  'success',
  (SELECT id FROM projects LIMIT 1),
  'gpt-4o-mini',
  '{"parent_trace_id": "parent-trace-001", "stage": "fact_extraction", "source": "Call Insights"}',
  1000,
  0.001,
  500,
  NOW()
),
(
  gen_random_uuid(),
  'child-trace-002',
  'call_insights_stage_2',
  'success',
  (SELECT id FROM projects LIMIT 1),
  'gpt-4o-mini',
  '{"parent_trace_id": "parent-trace-001", "stage": "reasoning", "source": "Call Insights"}',
  1500,
  0.0015,
  700,
  NOW()
),
(
  gen_random_uuid(),
  'child-trace-003',
  'call_insights_stage_3',
  'success',
  (SELECT id FROM projects LIMIT 1),
  'gpt-4o-mini',
  '{"parent_trace_id": "parent-trace-001", "stage": "summary", "source": "Call Insights"}',
  2000,
  0.002,
  900,
  NOW()
);
```

**Expected UI Display:**
- Parent trace: "parent-trace-001" with expand icon
- Aggregated: ∑ 4,500 tokens, ∑ $0.0045, Ø 700ms
- Blue badge: "Call Insights"
- When expanded: 3 children indented with stage badges

---

## 🎯 Final Validation

### Pre-Production Checklist

- [ ] Database migration applied successfully
- [ ] All 4 GIN indexes created
- [ ] Backend tests: 5/5 passing
- [ ] API server starts without errors
- [ ] UI loads without CORS errors
- [ ] Traces dashboard renders successfully
- [ ] Parent-child expansion works
- [ ] Source filtering works (all 3 sources)
- [ ] Aggregated metrics accurate
- [ ] Navigation to detail modals works
- [ ] Page load time < 200ms
- [ ] No N+1 query warnings
- [ ] Query plan shows index usage

### Production Deployment Steps

1. **Database Migration:**
   ```bash
   alembic upgrade head
   ```

2. **Verify Indexes:**
   ```sql
   SELECT COUNT(*) FROM pg_indexes
   WHERE tablename = 'traces'
   AND indexname LIKE 'idx_trace_metadata%';
   -- Expected: 4
   ```

3. **Deploy API:**
   - Restart API servers
   - Monitor logs for errors
   - Check health endpoint: `/health`

4. **Deploy UI:**
   - Build and deploy shell + mfe-traces
   - Clear CDN cache if applicable
   - Monitor browser console for errors

5. **Smoke Test:**
   - Load traces dashboard
   - Expand a parent trace
   - Filter by source
   - Check performance metrics

---

**Document Version:** 1.0
**Last Updated:** 2025-10-08
**Status:** ✅ READY FOR TESTING
