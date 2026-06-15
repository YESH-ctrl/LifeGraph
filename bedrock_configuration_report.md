# Bedrock Configuration Report

This report documents the audit of the AWS Bedrock configurations, providers, and routers in the Amazon Outcome Intelligence platform.

---

## 1. Configured Model IDs
Prior to migration, the following model identifiers were configured:
* **Sonnet Constant**: `anthropic.claude-3-sonnet` (inside `src/shared/ai/model_router.py`)
* **Haiku Constant**: `anthropic.claude-3-haiku` (inside `src/shared/ai/model_router.py`)
* **Connection Test Target**: `anthropic.claude-3-haiku` (inside `src/shared/ai/providers/bedrock_provider.py`)

*Audit Result*: These model IDs are either generic prefixes (e.g. `anthropic.claude-3-sonnet` instead of full IDs like `anthropic.claude-3-sonnet-20240229-v1:0`) or legacy models that require use-case form registration (`PENDING_USE_CASE_FORM`) on this account. This was the source of the `ValidationException` failures.

---

## 2. Region Configuration
* **Default Region**: `ap-south-1` (Mumbai)
* **Configuration Source**: Loaded dynamically via `os.environ.get("AWS_REGION", "ap-south-1")` inside `BedrockProvider` and `startup_security.py`.

*Audit Result*: Region `ap-south-1` is correct and resolves to the target deployment area.

---

## 3. Provider Mapping
* **Routing Map**: Mapped at the agent level within `ModelRouter.ROUTING_MAP`:
  * `mission` -> `HAIKU`
  * `cart` -> `SONNET`
  * `verification` -> `HAIKU`
  * `risk` -> `HAIKU`
  * `regret` -> `HAIKU`
  * `simulation` -> `SONNET`
  * `auditor` -> `SONNET`
* **Underlying Provider**: `BedrockProvider` handles connection setup, model invocation formatting via `ClaudeProvider`, and execution.

---

## 4. Credential Source
* **Initialization**: Handled in `BedrockProvider._initialize_client()` and `startup_security.py` using `boto3.Session().get_credentials()`.
* **Credential Loading**: Uses the standard AWS credential provider chain (reading from environment variables `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or the local AWS configuration profiles).

---

## 5. Fallback Logic
* **Silent Fallback Mechanism**:
  * On client initialization failure: Logs a warning and sets `self.local_mode = True`.
  * On connection test failure: Logs an error, sets `self.local_mode = True`, and returns `True` (hiding the error from downstream logic).
  * On invocation failure: Logs an error and returns `self._simulate_response(model_id, prompt, system_prompt)`.
* **Issue**: Any configuration error or credential failure causes the system to silently revert to Local Simulation Mode while reporting successful execution, leaving the user with simulated outputs without notice.

---

## 6. Migration Recommendations
1. **Enable Working Model Routing**: Map routing constants to successfully verified models on this AWS account (`meta.llama3-70b-instruct-v1:0` and `meta.llama3-8b-instruct-v1:0`).
2. **Implement Converse API**: Update `BedrockProvider` to use `converse()` to support multi-provider models seamlessly.
3. **Enforce Transparent Execution Modes**: Introduce `MODE=LOCAL_SIMULATION`, `MODE=BEDROCK_LIVE`, and `MODE=HYBRID`. Raise hard exceptions in `BEDROCK_LIVE` mode if Bedrock setup or invocation fails.
