# LifeGraph System Validation Report

_Generated: 2026-06-14 10:56:27 UTC_
_Branch: feature/demo-readiness_
_Base URL: http://127.0.0.1:8000_

## 📊 Executive Summary

| Metric       | Value |
| ------------ | ----- |
| Total Tests  | 30    |
| ✅ PASS      | 26    |
| ⚠️ PARTIAL   | 3     |
| ❌ FAIL      | 1     |
| 🎯 Pass Rate | 86.7% |

## 🚀 System Startup Information

```bash
# Navigate to src directory
cd d:\LifeGraph\src

# Start backend server
python -m uvicorn local_app:app --host 0.0.0.0 --port 8000 --reload
```

| Endpoint      | URL                                             |
| ------------- | ----------------------------------------------- |
| Backend       | http://localhost:8000                           |
| Swagger UI    | http://localhost:8000/docs                      |
| OpenAPI JSON  | http://localhost:8000/openapi.json              |
| Health (Docs) | http://localhost:8000/docs                      |
| System Status | http://localhost:8000/agents/system/status      |
| Agent Health  | http://localhost:8000/agents/debug/agent-health |
| Mission Debug | http://localhost:8000/mission/debug             |

## SECTION A: ✅ Working Features

### Health - Swagger UI

- **Status**: PASS
- **Details**: Swagger UI accessible

### Health - System Status (DynamoDB)

- **Status**: PASS
- **Details**: DynamoDB: 23 missions, 1665 products, 15 relationships. Models: embedding=amazon.titan-embed-text-v2, reranker=mock-reranker

### Health - Agent Diagnostics

- **Status**: PASS
- **Details**: Agent health diagnostics accessible

### Endpoint - Missions List

- **Status**: PASS
- **Details**: Listed missions. Count: 23

### Endpoint - Products List

- **Status**: PASS
- **Details**: Listed products. Count: 1665

### Endpoint - Users List

- **Status**: PASS
- **Details**: Users endpoint accessible

### Mission Detection - Biryani Query

- **Status**: PASS
- **Details**: Detected: chicken_biryani | Confidence: 0.73 | Params: {'guest_count': 10, 'audience': 'children'}

### Mission Detection - Movie Night

- **Status**: PASS
- **Details**: Detected: movie_night | Confidence: 0.64 | Params: {'guest_count': 1, 'audience': 'children'}

### Mission Detection - House Party

- **Status**: PASS
- **Details**: Detected: house_party | Confidence: 0.64 | Params: {'guest_count': 20, 'audience': 'children'}

### Verification - Biryani (empty cart)

- **Status**: PASS
- **Details**: Readiness=100% | Missing=[] | Critical Missing=[]

### Verification - Biryani (partial cart)

- **Status**: PASS
- **Details**: Readiness=100% | Missing=[] | Critical Missing=[]

### Verification - Scoring consistency

- **Status**: PASS
- **Details**: Readiness=100% | Missing=[] | Critical Missing=[]

### Risk Engine - Empty Cart

- **Status**: PASS
- **Details**: Overall Risk=25% | Completion Risk=0%

### Risk Engine - Partial Cart

- **Status**: PASS
- **Details**: Overall Risk=25% | Completion Risk=0%

### Prevention - Empty Cart

- **Status**: PASS
- **Details**: Checkout Allowed=True | Missing Dependencies=[]

### Prevention - Partial Items

- **Status**: PASS
- **Details**: Checkout Allowed=True | Missing Dependencies=[]

### Mission Graph - movie_night

- **Status**: PASS
- **Details**: Required=5, Optional=0, Dependencies=0

### Mission Graph - house_party

- **Status**: PASS
- **Details**: Required=5, Optional=0, Dependencies=0

### Simulator - Biryani 10 guests

- **Status**: PASS
- **Details**: Success Probability=100.0% | Warnings=0

### Simulator - Movie Night 5 guests

- **Status**: PASS
- **Details**: Success Probability=0.0% | Warnings=5

### Adaptive - Event Planner Persona

- **Status**: PASS
- **Details**: Shopper Type: Event Planner | Intervention: Suggest celebration essentials and quantity upgrades.

### Adaptive - Cooking Persona

- **Status**: PASS
- **Details**: Shopper Type: Student Shopper | Intervention: Focus on budget-friendly alternatives and study essentials.

### Memory - New User

- **Status**: PASS
- **Details**: Active=[], Completed=[], Recurring=[]

### Memory - Demo User

- **Status**: PASS
- **Details**: Active=[], Completed=[], Recurring=[]

### Orchestrator - Movie Night Pipeline

- **Status**: PASS
- **Details**: Checkout Allowed=False | Reason='Movie Night mission is only 23% ready. Missing critical items: Snn Popcorn Maize 1Kg Imported Raw Maize Popcorn Kernels 1Kg Ready To Cook High Expansion Homemade Healthy Snack, Toblerone Swiss Dark Tiny Chocolate 272 Gm 34 Pieces.' | Recommendations=['Add Snn Popcorn Maize 1Kg Imported Raw Maize Popcorn Kernels 1Kg Ready To Cook High Expansion Homemade Healthy Snack', 'Add Toblerone Swiss Dark Tiny Chocolate 272 Gm 34 Pieces', 'Add Too Yumm Multigrain Chips Dahi Papdi Chaat 54G']

### Schema Validation - All Response Fields

- **Status**: PASS
- **Details**: All schemas valid. Checked: verification: OK, risk: OK, orchestrator: OK

### Scenario: MOVIE_NIGHT

- **Status**: PASS
- **Details**: Full pipeline completed

## SECTION B: ❌ Broken Features

### Mission Graph - biryani_preparation

- **Status**: FAIL
- **Reason**: No products in graph for mission 'biryani_preparation'

## SECTION C: ⚠️ Warnings

### Health - Mission Debug (Bedrock)

- **Status**: PARTIAL
- **Reason**: Running in MOCK/Fallback mode. Available models: ['amazon.titan-embed-text-v2:0']

### Mission Detection - Generic Grocery

- **Status**: PARTIAL
- **Reason**: Expected 'grocer' but detected 'house_party' (confidence=0.46)

### Orchestrator - Biryani Pipeline

- **Status**: PARTIAL
- **Reason**: Fake product recommendations detected: ['Add Tilda Premium Basmati Rice 5 Kg', 'Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk']

### Scenario: CHICKEN_BIRYANI

- **Status**: PARTIAL
- **Reason**: Issues: ["Fake/generic recommendations: ['Add Tilda Premium Basmati Rice 5 Kg', 'Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk']"]

### Scenario: HOUSE_PARTY

- **Status**: PARTIAL
- **Reason**: Issues: ["Fake/generic recommendations: ['Add Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O']"]

## SECTION D: 🚨 Demo Blockers

- **Mission Graph - biryani_preparation**: No products in graph for mission 'biryani_preparation'
- **Health - Mission Debug (Bedrock)**: Running in MOCK/Fallback mode. Available models: ['amazon.titan-embed-text-v2:0']
- **Mission Detection - Generic Grocery**: Expected 'grocer' but detected 'house_party' (confidence=0.46)
- **Orchestrator - Biryani Pipeline**: Fake product recommendations detected: ['Add Tilda Premium Basmati Rice 5 Kg', 'Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk']
- **Scenario: CHICKEN_BIRYANI**: Issues: ["Fake/generic recommendations: ['Add Tilda Premium Basmati Rice 5 Kg', 'Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk']"]
- **Scenario: HOUSE_PARTY**: Issues: ["Fake/generic recommendations: ['Add Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O']"]

## SECTION E: 🎬 Recommended Demo Flow

### For Judges — Step-by-Step Demo

1. **Open Swagger UI** → http://localhost:8000/docs
2. **Check System Status** → `GET /agents/system/status`
3. **Mission Detection Demo**:
   ```
   POST /agents/mission-detection/test
   {"query": "I want to cook chicken biryani for 10 people tonight"}
   ```
4. **Orchestrator Full Pipeline**:
   ```
   POST /agents/orchestrator/test
   {"query": "I want to cook chicken biryani for 10 people tonight"}
   ```
5. **Verify Readiness Score** — Check `readiness_score` in verification response
6. **Risk Score** — Check `overall_risk` in risk response
7. **Checkout Decision** — Check `final_decision.checkout_allowed` and `reason`

## SECTION E (cont.): 🎯 Curated Mission Results

### ⚠️ CHICKEN_BIRYANI

- **Query**: `I want to cook chicken biryani for 10 people tonight`
- **Detected Mission**: `chicken_biryani`
- **Confidence**: `0.74`
- **Parameters**: `{'guest_count': 10, 'audience': 'children'}`
- **Readiness Score**: `23%`
- **Risk Score**: `40%`
- **Graph Products**: Required=5, Optional=0
- **Checkout Allowed**: `False`
- **Decision Reason**: Chicken Biryani mission is only 23% ready. Missing critical items: Dc10Fe0A-3B8C-42Be-9F10-Cb14867358B0, Tilda Premium Basmati Rice 5 Kg.
- **Recommendations**: ['Add Masala Combo - Chicken 15 Gm + Meat 15 Gm + Punjabi Butter Chicken 15 Gm + Garam Masala 40 Gm', 'Add Tilda Premium Basmati Rice 5 Kg', 'Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk']
- **Issues Found**: ["Fake/generic recommendations: ['Add Tilda Premium Basmati Rice 5 Kg', 'Add House Of Saffron 1 Gram Pure Kashmir Mogra Kesar Premium Original Saffron For Pregnant Women Milk Biryani Cooking Sk']"]

### ✅ MOVIE_NIGHT

- **Query**: `planning a movie night at home for 5 friends this weekend`
- **Detected Mission**: `movie_night`
- **Confidence**: `0.63`
- **Parameters**: `{'guest_count': 5, 'audience': 'children', 'event_date': 'this weekend'}`
- **Readiness Score**: `23%`
- **Risk Score**: `40%`
- **Graph Products**: Required=5, Optional=0
- **Checkout Allowed**: `False`
- **Decision Reason**: Movie Night mission is only 23% ready. Missing critical items: Snn Popcorn Maize 1Kg Imported Raw Maize Popcorn Kernels 1Kg Ready To Cook High Expansion Homemade Healthy Snack, Toblerone Swiss Dark Tiny Chocolate 272 Gm 34 Pieces.
- **Recommendations**: ['Add Snn Popcorn Maize 1Kg Imported Raw Maize Popcorn Kernels 1Kg Ready To Cook High Expansion Homemade Healthy Snack', 'Add Toblerone Swiss Dark Tiny Chocolate 272 Gm 34 Pieces', 'Add Too Yumm Multigrain Chips Dahi Papdi Chaat 54G']

### ⚠️ HOUSE_PARTY

- **Query**: `hosting a house party for 20 guests next Saturday`
- **Detected Mission**: `house_party`
- **Confidence**: `0.62`
- **Parameters**: `{'guest_count': 20, 'audience': 'children', 'event_date': 'next saturday'}`
- **Readiness Score**: `23%`
- **Risk Score**: `40%`
- **Graph Products**: Required=5, Optional=0
- **Checkout Allowed**: `False`
- **Decision Reason**: House Party mission is only 23% ready. Missing critical items: Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O, Mr Makhana Roasted Makhana Foxnuts Pudina Party Cream Onion Butter Tomato Pack Of 3X75 Gm Gluten Free Msg F.
- **Recommendations**: ['Add Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O', 'Add Mr Makhana Roasted Makhana Foxnuts Pudina Party Cream Onion Butter Tomato Pack Of 3X75 Gm Gluten Free Msg F', 'Add Pizza Cheese - Mozzarella, Diced']
- **Issues Found**: ["Fake/generic recommendations: ['Add Happilo Premium International Salted Partymix 200G Healthy Dry Fruits Snack Contains Kaju Kishmish Badam Pista O']"]

## SECTION F: 🔧 Exact Testing Commands

### Server Startup

```powershell
cd d:\LifeGraph\src
python -m uvicorn local_app:app --host 0.0.0.0 --port 8000 --reload
```

### Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/agents/system/status" -Method GET
```

### Mission Detection — Biryani

```powershell
$body = '{"query": "I want to cook chicken biryani for 10 people tonight"}'
Invoke-RestMethod -Uri "http://localhost:8000/agents/mission-detection/test" -Method POST -Body $body -ContentType 'application/json'
```

### Full Orchestrator Pipeline — Movie Night

```powershell
$body = '{"query": "planning a movie night at home for 5 friends"}'
Invoke-RestMethod -Uri "http://localhost:8000/agents/orchestrator/test" -Method POST -Body $body -ContentType 'application/json'
```

### Graph Check — House Party

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/agents/graph/mission/house_party" -Method GET
```

### Run This Validation Script

```powershell
cd d:\LifeGraph\src
python ..\scripts\full_validation.py
```

---

_Report generated by LifeGraph QA Validation Suite_
