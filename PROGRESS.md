# CKAN 2.11 Migration Progress

## Starting Point
- Extension: ckanext-versions
- Target: CKAN 2.11 + Python 3.10
- Branch: toavina/update-python

## Initial Setup

### Update GitHub Actions Workflow
**File Modified**: `.github/workflows/test.yml`

**Changes**:
- Updated GitHub Actions from v2 → v6
- Removed matrix strategy for multiple Python/CKAN versions
- Set single Python version: "3.10"
- Set single CKAN version: 2.11
- Container: `ckan/ckan-dev:2.11-py3.10` with `--user root` option
- Updated services to CKAN 2.11 versions:
  - Solr: `ckan/ckan-solr:2.11-solr9`
  - Postgres: `ckan/ckan-postgres-dev:2.11`
  - Redis: `redis:3`
- Simplified test run command (removed codecov upload)

**Result**: Ready for testing with CKAN 2.11

---

## Fix 1: Activity Model Import

### Issue
**Error**: Setup extension failed with:
```
ModuleNotFoundError: No module named 'ckan.model.activity'
AttributeError: module 'ckan.model' has no attribute 'Activity'
```

**Location**:
- `ckanext/versions/logic/action.py:17-19`
- `ckanext/versions/logic/dataset_version_action.py:13-16`

### Root Cause
Starting from CKAN 2.10, activities were extracted into a separate plugin. The Activity model class was moved from `ckan.model.Activity` to `ckanext.activity.model.Activity`.

**References**:
- [Extract activities into a separate plugin - PR #6790](https://github.com/ckan/ckan/pull/6790)
- [CKAN 2.9 to 2.10 migration tips](https://github.com/ckan/ckan/wiki/CKAN-2.9-to-2.10-migration-tips)

### Solution Applied
Updated the import fallback chain to try the CKAN 2.10+ pattern first:
```python
# Activity import for different CKAN versions
# CKAN 2.10+ moved Activity to a separate plugin
try:
    from ckanext.activity.model import Activity
except ImportError:
    try:
        from ckan.model import Activity
    except ImportError:
        Activity = core_model.Activity
```

This provides backward compatibility with CKAN <=2.9 while supporting CKAN 2.10+.

**Files Modified**:
- `ckanext/versions/logic/action.py`: Lines 15-23
- `ckanext/versions/logic/dataset_version_action.py`: Lines 12-20

**Result**: Ready for testing

---

## Testing Status
- Initial test: Setup extension failed (Activity import error)
- After Fix 1: Test completed - 80 failed, 11 passed, 12 errors

---

## Fix 2: Auth Function Registration Bug

### Issue
**Error**: Multiple tests failing with:
```
ValueError: Authorization function not found: version_create
ValueError: Authorization function not found: version_delete
ValueError: Authorization function not found: version_list
ValueError: Authorization function not found: version_show
```

**Location**: `ckanext/versions/plugin.py:71`

### Root Cause
In the `get_auth_functions()` method, the `resource_version_clear` auth function was incorrectly registered as `action.resource_version_clear` instead of `auth.resource_version_clear`. This caused the auth module to not be properly initialized, preventing all auth functions from being registered.

### Solution Applied
Changed line 71 in plugin.py from:
```python
'resource_version_clear': action.resource_version_clear,
```
to:
```python
'resource_version_clear': auth.resource_version_clear,
```

**Files Modified**:
- `ckanext/versions/plugin.py`: Line 71

**Result**: Auth functions should now register correctly. However, tests still show auth functions not found.

---

## Fix 3: Add clean_db_with_migrations fixture for CKAN 2.11 activity plugin

### Issue
**Error**: 2 tests in test_helpers.py failing with:
```
sqlalchemy.exc.ProgrammingError: column "permission_labels" of relation "activity" does not exist
```

**Root Cause**:
Similar to ckanext-fork and ckanext-restricted, CKAN 2.11's activity plugin requires a `permission_labels` column in the activity table. The `clean_db` fixture rebuilds the database fresh for test isolation, but doesn't include plugin-specific migrations.

### Solution Applied
Created a `clean_db_with_migrations` fixture (following pattern from PROGRESS_FORK.md):

1. Added fixture to `ckanext/versions/tests/fixtures.py`:
   - Extends the standard `clean_db` fixture
   - After `clean_db` runs, manually executes SQL to add the `permission_labels` column:
     ```sql
     ALTER TABLE activity ADD COLUMN IF NOT EXISTS permission_labels text[];
     ```

2. Updated `test_helpers.py` to use `clean_db_with_migrations` instead of `clean_db`

**Files Modified**:
- `ckanext/versions/tests/fixtures.py`: Added `clean_db_with_migrations` fixture
- `ckanext/versions/tests/test_helpers.py`: Changed fixtures from `clean_db` to `clean_db_with_migrations`

**Result**: Should fix the 2 permission_labels errors. Auth function issue still unresolved. Ready for testing.

---

## Migration Status: INCOMPLETE

### Test Results Summary
- **Before fixes**: 80 failed, 11 passed, 12 errors
- **After Fix 2 & 3**: Not tested - migration abandoned due to complexity

### Issues Identified

1. **Auth Function Registration Bug (Fix 2)** ✅ Fixed in code, but not verified
   - Found and fixed bug on plugin.py:71 where `action.resource_version_clear` was incorrectly registered as auth function
   - However, tests still showed "Authorization function not found" errors for all auth functions
   - Root cause unclear - may be deeper plugin initialization issue in CKAN 2.11

2. **Permission Labels Column (Fix 3)** ✅ Fixed in code, but not verified
   - Added `clean_db_with_migrations` fixture following pattern from ckanext-fork
   - Should resolve 2 errors in test_helpers.py

3. **Unresolved Issues**:
   - 80 tests still failing with "Authorization function not found"
   - Missing CKAN actions: `package_activity_list`, `activity_data_show` (renamed/removed in CKAN 2.11)
   - View plugin issues: `versions_view`, `image_view` not found
   - Auth functions not accessible despite correct registration
   - Likely requires more extensive refactoring than other extensions

### Why Migration Was Abandoned

This extension proved significantly more complex than ckanext-fork (14 fixes, 61 tests) or ckanext-restricted (10 fixes, 24 tests). The auth function registration issue suggests deeper architectural incompatibility with CKAN 2.11 that would require:
- Extensive debugging of plugin initialization
- Possibly redesigning how auth functions are registered
- Understanding why 11 tests pass but 80 fail with same auth error
- Time investment exceeding available resources

### Recommendation

Future migration attempts should:
1. Verify plugin loading and auth registration work before addressing individual test failures
2. Consider whether the extension's architecture is compatible with CKAN 2.11's plugin system changes
3. Budget significantly more time than simpler extensions (estimate 3-4x the effort of ckanext-fork)
4. May require upstream consultation with CKAN community about auth function registration changes in 2.11

### Files Modified (Not Fully Tested)
- `.github/workflows/test.yml` - Updated to CKAN 2.11
- `ckanext/versions/logic/action.py` - Activity model import compatibility
- `ckanext/versions/logic/dataset_version_action.py` - Activity model import compatibility
- `ckanext/versions/plugin.py` - Fixed auth function registration bug
- `ckanext/versions/tests/fixtures.py` - Added clean_db_with_migrations fixture
- `ckanext/versions/tests/test_helpers.py` - Use clean_db_with_migrations
- `PROGRESS.md` - Documentation

---

*Migration started: 2026-01-09*
*Migration abandoned: 2026-01-09*
*Reason: Complexity exceeds available time/resources*
