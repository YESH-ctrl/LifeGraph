# LifeGraph Post-Merge Integration & AWS Readiness Audit

**Date**: 2026-06-14  
**Auditor**: Antigravity AI  
**Status**: NOT READY FOR DEMO  

---

## 1. Git Status & Merge/Conflict Status

### Git Working Tree Status
- **Current Branch**: `main` (synchronized and up-to-date with `origin/main`).
- **Latest Commit**: `a2e26c1a8e4d3f11e06680b0bd850cd8e75a438a` — *"Reloaded with the dataset"* by YESH-Ctrl (Sun Jun 14 13:11:23 2026).
- **Merge PR #4 Present**: Confirmed. The merge commit `3d01c85` (*"Merge pull request #4 from YESH-ctrl/feature/verification-risk"*) is present in the main history.
- **Local Modifications**: `src/infrastructure/dynamodb/base_repository.py` is modified locally to replace prefix starts_with query logic with exact match (`.eq()`) on DynamoDB `SK`.

### Merge Conflict Resolutions
The conflicts from the merge of `feature/verification-risk` into `main` were resolved in commit `00fbe15`. However, the resolution preserved two conflicting implementations of the Risk Service, which is the root cause of the current integration failures.

---

## 2. AWS Compatibility Status

The DynamoDB table `LifeGraph` and AWS Bedrock connections are fully operational:
- **Bedrock Integration**: The Bedrock Client handles embedding generation. In environments without AWS credentials, it safely and deterministically falls back to local 1024-dimensional mock embeddings, ensuring the test suite can run successfully without external dependencies.
- **DynamoDB Single-Table Design**: The table structure properly supports the V2 single-table design with GSI1 and GSI2 indices.

---

## 3. Dataset Compatibility Status

- **Production Dataset**: The new production dataset `src/data_ingestion/All Grocery and Gourmet Foods.csv` contains over 960 rows, representing the expanded catalog.
- **Test Ingestion Purge**: **CRITICAL ISSUE**: The test `test_admin_endpoints_mock` in `tests/test_admin_pipeline.py` executes a full scan and purge of the DynamoDB table on initialization:
  ```python
  # Clear the database first to ensure a clean test state
  response = table.scan(...)
  with table.batch_writer() as batch:
      for item in items:
          batch.delete_item(Key={"PK": item["PK"], "SK": item["SK"]})
  ```
  Consequently, running the test suite wipes out the entire production dataset and leaves only 11 mock items in the database, breaking the live system's state.

---

## 4. Graph & Schema Compatibility Status

We identified two major schema/type compatibility blockers introduced in the merge:

### Blocker A: Risk Response Type Mismatch (400 Bad Request)
- **Problem**: `OrchestratorService` (in `src/agents/orchestrator/service.py`) imports and calls `domains.risk.service.RiskService`.
- **Mismatch**: 
  - `domains.risk.service.RiskService` returns strings (`"LOW"`, `"HIGH"`, `"MEDIUM"`) for its risk dimensions (`quantity_risk`, `compatibility_risk`, `budget_risk`, `timing_risk`).
  - The `RiskResult` response schema (in `src/agents/orchestrator/schemas.py`) expects these fields to be **integers** (0-100), as designed in V2:
    ```python
    class RiskResult(BaseModel):
        overallRisk: str
        completionRisk: int = 0
        quantityRisk: int = 0
        ...
    ```
- **Impact**: Any checkout execution request via `/mission/execute` returns a `400 Bad Request` validation error because Pydantic fails to parse `"LOW"` as an integer:
  ```json
  "details": [{
      "type": "int_parsing",
      "loc": ["quantityRisk"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "LOW"
  }]
  ```

### Blocker B: `missionHints` Format Mismatch (AttributeError)
- **Problem**: In the reloaded dataset, products were seeded with `missionHints` as a list of dictionaries containing scores:
  ```json
  "missionHints": [
      {"score": 0.99, "mission": "biryani_preparation"},
      {"score": 0.6, "mission": "paneer_butter_masala_dinner"}
  ]
  ```
- **Mismatch**: The mission mapping pipeline (`src/data_ingestion/mission_mapper.py` line 34) expects `missionHints` to be a list of strings:
  ```python
  hints = [h.lower() for h in product.get("missionHints", [])]
  ```
- **Impact**: Calling `/admin/enrich-products` or `/admin/import-missions` fails with `AttributeError: 'dict' object has no attribute 'lower'`, preventing the missions from being rebuilt or mapped.

---

## 5. Test Results

Running `pytest tests/ -v` yields:
- **Passed**: 50 tests.
- **Failed**: 2 integration tests (`tests/test_orchestrator_integration.py`):
  - `test_happy_path_mission_execute` (Failed with `400 Bad Request`)
  - `test_high_risk_and_incomplete_cart` (Failed with `400 Bad Request`)

---

## 6. Risks & Blockers

1. **Production Data Erasure**: Any automated test run completely deletes the live database contents.
2. **Broken checkout API**: The API endpoint `/mission/execute` is currently completely broken due to the risk string-to-int validation error.
3. **Broken Data Enrichment**: The data enrichment/ingestion pipeline is blocked by the dict/string type mismatch in product `missionHints`.

---

## 7. Exact Next Actions

To make the codebase demo-ready, the following fixes are required:
1. **Fix `domains/risk/service.py`**:
   Update `RiskService.analyze` to return integers (0-100) instead of `"LOW"`/`"HIGH"` strings for the 4 risk dimensions, matching the V2 `RiskResponseData` schema in `shared/schemas/engine_schemas.py`.
2. **Fix `src/data_ingestion/mission_mapper.py`**:
   Modify `map_products_to_mission` to handle `missionHints` whether they are strings or dicts:
   ```python
   hints = []
   for h in product.get("missionHints", []):
       if isinstance(h, dict):
           hints.append(h.get("mission", "").lower())
       else:
           hints.append(h.lower())
   ```
3. **Isolate Test Database**:
   Modify tests to either use a mocked DynamoDB backend or use a separate table name (e.g. `LifeGraphTest`) to prevent them from deleting production data.

---

## Verdict

### **NOT READY FOR DEMO**

**Explanation**: While the individual agent logic and database models have been updated to V2, the system cannot be demoed because the main checkout endpoint `/mission/execute` is broken (returning `400 Bad Request`) due to schema mismatches, and the database seeding is blocked by an `AttributeError` in the ingestion pipeline.
