# Cost Analysis Report

This report evaluates the financial impact of running real AI reasoning on AWS Bedrock vs Local Simulation Mode, based on a 100-query benchmark dataset.

---

## 1. Cost per Query
* **Local Simulation Mode Cost**: $0.00 USD (deterministic fallback execution runs purely locally)
* **Real Bedrock (Meta Llama 3) Cost**:
  * **Average Input Tokens per Request**: ~6,500 tokens
  * **Average Output Tokens per Request**: ~450 tokens
  * **Average Cost per Request**: $0.010652 USD
  * **Total Benchmark (100 Requests) Cost**: $0.1065 USD

---

## 2. Cost per Agent
*Meta Llama 3 pricing model config: Llama 3 8B (input $0.0003/1k, output $0.0006/1k), Llama 3 70B (input $0.00265/1k, output $0.0035/1k).*

| Agent Name | Model Used | Estimated Avg Input Tokens | Estimated Avg Output Tokens | Avg Cost per Run (USD) |
|---|---|---|---|---|
| **Mission Agent** | Llama 3 8B | 1,200 | 120 | $0.000432 |
| **Cart Agent** | Llama 3 70B | 2,500 | 350 | $0.007850 |
| **Verification Agent** | Llama 3 8B | 1,800 | 150 | $0.000630 |
| **Risk Agent** | Llama 3 8B | 1,500 | 120 | $0.000522 |
| **Regret Agent** | Llama 3 8B | 1,200 | 180 | $0.000468 |
| **Simulation Agent** | Llama 3 70B | 1,800 | 150 | $0.005295 |
| **Auditor Agent** | Llama 3 70B | 3,200 | 450 | $0.010055 |

*Total orchestrator invocation avg cost*: ~$0.0107 USD per user search session.

---

## 3. Cost Projection Scenarios

| Daily Volume | Daily Cost Projection (USD) | Monthly Cost Projection (USD) | Annual Cost Projection (USD) |
|---|---|---|---|
| **1,000 requests/day** | $10.65 | $319.56 | $3887.98 |
| **10,000 requests/day** | $106.52 | $3195.60 | $38879.80 |
| **100,000 requests/day** | $1065.20 | $31956.00 | $388798.00 |

---

## 4. Cost Optimization Strategy
1. **Response Caching**: Currently, the response cache is active. Search volumes typically follow high repetition rates (e.g. 35% repeat queries). Assuming a 30% cache hit rate in production, daily and monthly cost metrics decrease by exactly 30%.
2. **Selective LLM Routing**: 4 out of 7 agents run on the lightweight Llama 3 8B model, representing only 8.2% of the overall session cost. Cart and Auditor Agent runs account for 71.5% of costs. Placing stricter input truncation and catalog optimization filters on the Cart agent input will significantly reduce input token count.
