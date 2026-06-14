import json
from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, File
from pydantic import ValidationError, BaseModel
from core.exceptions import LifeGraphException

from api.controllers.user_controller import UserController
from api.controllers.product_controller import ProductController
from api.controllers.cart_controller import CartController
from api.controllers.verification_controller import VerificationController
from api.controllers.risk_controller import RiskController
from api.controllers.prevention_controller import PreventionController
from api.controllers.mission_controller import MissionController
from domains.mission_detection.controller import MissionDetectionController
from api.controllers.relationship_controller import RelationshipController
from api.controllers.graph_controller import GraphController
from api.controllers.workflow_controller import WorkflowController

from domains.users.schemas import UserCreate, UserUpdate
from domains.products.schemas import ProductCreate, ProductUpdate
from domains.carts.schemas import CartCreate, CartUpdate, CartAddItem
from domains.memory.controller import MemoryController
from domains.adaptive.controller import AdaptiveController
from domains.simulator.controller import SimulatorController
from domains.memory.schemas import MissionStateRequest
from domains.adaptive.schemas import AdaptiveRequest
from domains.simulator.schemas import SimulatorRequest
from shared.schemas.engine_schemas import VerificationRequest, RiskRequest, PreventionRequest, WorkflowCheckoutRequest
from domains.mission_detection.schemas import MissionDetectionRequest
from shared.schemas.mission_schemas import MissionCreate, MissionUpdate
from shared.schemas.relationship_schemas import RelationshipCreate

from agents.orchestrator.controller import OrchestratorController
from agents.orchestrator.schemas import MissionExecutionRequest

# Seeder imports removed

app = FastAPI(
    title="Amazon LifeGraph",
    version="1.0.0",
    description="Local verification environment for LifeGraph APIs"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_ctrl = UserController()
product_ctrl = ProductController()
cart_ctrl = CartController()
memory_ctrl = MemoryController()
adaptive_ctrl = AdaptiveController()
simulator_ctrl = SimulatorController()
verification_ctrl = VerificationController()
risk_ctrl = RiskController()
prevention_ctrl = PreventionController()
mission_ctrl = MissionController()
mission_detection_ctrl = MissionDetectionController()
relationship_ctrl = RelationshipController()
graph_ctrl = GraphController()
workflow_ctrl = WorkflowController()
orchestrator_ctrl = OrchestratorController()
# seeder_ctrl removed

async def create_event(request: Request, payload: BaseModel = None) -> dict:
    """Adapts a FastAPI Request into an AWS API Gateway event format."""
    try:
        if payload:
            body = payload.model_dump_json()
        else:
            body_bytes = await request.body()
            body = body_bytes.decode('utf-8') if body_bytes else '{}'
    except Exception:
        body = '{}'
        
    return {
        'path': request.url.path,
        'httpMethod': request.method,
        'body': body,
        'pathParameters': request.path_params,
        'queryStringParameters': dict(request.query_params) if request.query_params else None,
    }

def handle_controller_response(response: Response, result: dict):
    """Parses controller result and sets status code and content."""
    response.status_code = result.get('statusCode', 200)
    body_str = result.get('body', '{}')
    try:
        return json.loads(body_str)
    except json.JSONDecodeError:
        return body_str

def handle_exception(e: Exception, response: Response):
    if isinstance(e, ValidationError):
        response.status_code = 400
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload",
                "details": e.errors()
            }
        }
    elif isinstance(e, LifeGraphException):
        response.status_code = e.status_code
        return {
            "success": False,
            "error": {
                "code": e.code,
                "message": e.message
            }
        }
    else:
        response.status_code = 500
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }

# --- Users ---
@app.get("/users")
async def list_users(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = user_ctrl.list_users(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/users")
async def create_user(payload: UserCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = user_ctrl.create_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/users/{id}")
async def get_user(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = user_ctrl.get_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/users/{id}")
async def update_user(id: str, payload: UserUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = user_ctrl.update_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/users/{id}")
async def delete_user(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = user_ctrl.delete_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Products ---
@app.get("/products")
async def list_products(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = product_ctrl.list_products(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/products")
async def create_product(payload: ProductCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = product_ctrl.create_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/products/{id}")
async def get_product(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = product_ctrl.get_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/products/{id}")
async def update_product(id: str, payload: ProductUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = product_ctrl.update_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/products/{id}")
async def delete_product(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = product_ctrl.delete_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Carts ---
@app.get("/carts")
async def list_carts(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.list_carts(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/carts")
async def create_cart(payload: CartCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = cart_ctrl.create_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/carts/{id}")
async def get_cart(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.get_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/carts/{id}")
async def update_cart(id: str, payload: CartUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = cart_ctrl.update_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/carts/{id}")
async def delete_cart(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.delete_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/carts/{id}/items")
async def add_cart_item(id: str, payload: CartAddItem, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = cart_ctrl.add_item(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Memory ---
@app.get("/memory/active/{user_id}")
async def get_active_missions(user_id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = memory_ctrl.get_active_missions(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/memory/history/{user_id}")
async def get_mission_history(user_id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = memory_ctrl.get_mission_history(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/memory/track")
async def track_mission(payload: MissionStateRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = memory_ctrl.track_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Adaptive ---
@app.post("/adaptive/analyze")
async def analyze_behavior(payload: AdaptiveRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = adaptive_ctrl.analyze_behavior(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/adaptive/profile")
async def get_shopper_profile(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = adaptive_ctrl.get_shopper_profile(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Simulator ---
@app.post("/simulator/run")
async def simulate_mission(payload: SimulatorRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = simulator_ctrl.simulate_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/simulator/probability")
async def get_success_probability(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = simulator_ctrl.get_success_probability(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Verification ---
@app.post("/verification/verify")
async def verify(request: Request, response: Response, payload: VerificationRequest):
    event = await create_event(request, payload)
    try:
        res = verification_ctrl.verify(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Risk ---
@app.post("/risk/analyze")
async def analyze(request: Request, response: Response, payload: RiskRequest):
    event = await create_event(request, payload)
    try:
        res = risk_ctrl.analyze(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Prevention ---
@app.post("/prevent-checkout")
async def evaluate(request: Request, response: Response, payload: PreventionRequest):
    event = await create_event(request, payload)
    try:
        res = prevention_ctrl.evaluate(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Mission Detection ---
from domains.missions.detection_service import DetectionService

detection_service = DetectionService()

class DetectionRequest(BaseModel):
    query: str

@app.post("/mission/detect")
async def detect_mission(payload: DetectionRequest, response: Response):
    try:
        res = detection_service.detect_mission(payload.query)
        if not res.get("success", False):
            response.status_code = 400
        return res
    except Exception as e:
        response.status_code = 500
        return {"success": False, "error": str(e)}

@app.get("/mission/debug")
async def get_mission_debug():
    try:
        return detection_service.get_debug_diagnostics()
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Missions ---
@app.get("/missions")
async def list_missions(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = mission_ctrl.list_missions(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/missions")
async def create_mission(payload: MissionCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = mission_ctrl.create_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/missions/{id}")
async def get_mission(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = mission_ctrl.get_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/missions/{id}")
async def update_mission(id: str, payload: MissionUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = mission_ctrl.update_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/missions/{id}")
async def delete_mission(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = mission_ctrl.delete_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Relationships ---
@app.get("/relationships")
async def list_relationships(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = relationship_ctrl.list_relationships(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/relationships")
async def create_relationship(payload: RelationshipCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = relationship_ctrl.create_relationship(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/relationships/{id}")
async def delete_relationship(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = relationship_ctrl.delete_relationship(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Graph ---
@app.get("/missions/{id}/requirements")
async def get_mission_requirements(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_mission_requirements(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/products/{id}/dependencies")
async def get_product_dependencies(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_product_dependencies(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/products/{id}/substitutes")
async def get_product_substitutes(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_product_substitutes(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Workflows ---
@app.post("/workflows/checkout")
async def run_checkout_workflow(request: Request, response: Response, payload: WorkflowCheckoutRequest):
    event = await create_event(request, payload)
    try:
        res = workflow_ctrl.run_checkout_workflow(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Mission Orchestrator ---
@app.post("/mission/execute")
async def execute_mission(payload: MissionExecutionRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = orchestrator_ctrl.execute_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Admin Ingestion Routes ---
@app.post("/admin/import-products", tags=["Admin"])
async def import_products(file: UploadFile = File(...)):
    from data_ingestion.pipeline import import_products_from_bytes
    try:
        content = await file.read()
        res = import_products_from_bytes(content, file.filename)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/import-missions", tags=["Admin"])
async def import_missions():
    from data_ingestion.pipeline import import_missions_pipeline
    try:
        res = import_missions_pipeline()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/data-quality-report", tags=["Admin"])
async def data_quality_report():
    from data_ingestion.pipeline import generate_data_quality_report
    try:
        res = generate_data_quality_report()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/enrich-products", tags=["Admin"])
async def enrich_products():
    from data_ingestion.pipeline import enrich_products_pipeline
    try:
        res = enrich_products_pipeline()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Agents Swagger Testing Layer ---
from shared.schemas.agent_test_schemas import (
    MissionDetectionTestRequest, MissionDetectionTestResponse,
    VerificationTestRequest, VerificationTestResponse,
    RiskTestRequest, RiskTestResponse,
    SimulatorTestRequest, SimulatorTestResponse,
    PreventionTestRequest, PreventionTestResponse,
    MemoryTestRequest, MemoryTestResponse,
    AdaptiveTestRequest, AdaptiveTestResponse,
    GraphMissionResponse,
    OrchestratorTestRequest, OrchestratorTestResponse,
    SystemStatusResponse
)
from domains.missions.agent_test_service import AgentTestService

agent_test_service = AgentTestService()

@app.post("/agents/mission-detection/test", response_model=MissionDetectionTestResponse, tags=["Agents"])
async def test_mission_detection(payload: MissionDetectionTestRequest):
    try:
        return agent_test_service.test_mission_detection(payload.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/verification/test", response_model=VerificationTestResponse, tags=["Agents"])
async def test_verification(payload: VerificationTestRequest):
    try:
        return agent_test_service.test_verification(payload.mission_id, payload.products)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/risk/test", response_model=RiskTestResponse, tags=["Agents"])
async def test_risk(payload: RiskTestRequest):
    try:
        return agent_test_service.test_risk(payload.mission_id, payload.products)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/simulator/test", response_model=SimulatorTestResponse, tags=["Agents"])
async def test_simulator(payload: SimulatorTestRequest):
    try:
        products_input = [{"product": p.product, "quantity": p.quantity} for p in payload.products]
        return agent_test_service.test_simulator(payload.mission_id, payload.guest_count, products_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/prevention/test", response_model=PreventionTestResponse, tags=["Agents"])
async def test_prevention(payload: PreventionTestRequest):
    try:
        return agent_test_service.test_prevention(payload.products)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/memory/test", response_model=MemoryTestResponse, tags=["Agents"])
async def test_memory(payload: MemoryTestRequest):
    try:
        return agent_test_service.test_memory(payload.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/adaptive/test", response_model=AdaptiveTestResponse, tags=["Agents"])
async def test_adaptive(payload: AdaptiveTestRequest):
    try:
        return agent_test_service.test_adaptive(
            payload.user_id,
            mission_id=payload.mission_id or "",
            mission_category=payload.mission_category or "",
            cart_size=payload.cart_size or 0,
            urgency=payload.urgency or "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/graph/mission/{mission_id}", response_model=GraphMissionResponse, tags=["Agents"])
async def test_graph(mission_id: str):
    try:
        return agent_test_service.test_graph(mission_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/orchestrator/test", response_model=OrchestratorTestResponse, tags=["Agents"])
async def test_orchestrator(payload: OrchestratorTestRequest):
    try:
        return agent_test_service.test_orchestrator(payload.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/system/status", response_model=SystemStatusResponse, tags=["Agents"])
async def test_system_status():
    try:
        return agent_test_service.test_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Phase 8: Diagnostics Endpoints ---
@app.get("/agents/debug/agent-health", tags=["Diagnostics"])
async def agent_health():
    """Returns V2 data consumption status for all agents."""
    from graph.service import GraphService
    gs = GraphService()
    
    # Check if a sample mission has V2 data
    sample_mission = "birthday_party"
    has_weights = len(gs.get_mission_requirements_weighted(sample_mission)) > 0
    has_rules = len(gs.get_mission_rules(sample_mission)) > 0
    has_intents = len(gs.get_mission_intents(sample_mission)) > 0
    has_metadata = gs.get_mission_metadata(sample_mission) is not None
    
    return {
        "verification": {
            "using_v2_weights": True,
            "graph_has_weighted_requirements": has_weights,
        },
        "risk": {
            "using_v2_rules": True,
            "graph_has_rules": has_rules,
            "dimensions": ["completion", "quantity", "compatibility", "timing", "budget"],
        },
        "simulator": {
            "using_simulation_rules": True,
            "graph_has_rules": has_rules,
        },
        "adaptive": {
            "using_user_history": True,
            "personas": ["Event Planner", "Festival Shopper", "Monthly Grocery Shopper",
                         "Travel Planner", "Student Shopper", "Health Focused Shopper",
                         "Emergency Buyer", "Research Buyer"],
        },
        "memory": {
            "using_v2_mission_records": True,
            "schema": "USER#{user_id} / MISSION#ACTIVE#{id} | MISSION#COMPLETED#{id}",
        },
    }

@app.get("/agents/debug/mission/{mission_id}", tags=["Diagnostics"])
async def debug_mission(mission_id: str):
    """Returns full V2 graph data for a mission."""
    from graph.service import GraphService
    gs = GraphService()
    
    metadata = gs.get_mission_metadata(mission_id)
    weighted_reqs = gs.get_mission_requirements_weighted(mission_id)
    rules = gs.get_mission_rules(mission_id)
    parameters = gs.get_mission_parameters(mission_id)
    intents = gs.get_mission_intents(mission_id)
    synonyms = gs.get_mission_synonyms(mission_id)
    requirements = gs.get_mission_requirements(mission_id)

    # Classify requirements by priority
    critical = [r for r in weighted_reqs if r.get("priority", "IMPORTANT") == "CRITICAL"]
    important = [r for r in weighted_reqs if r.get("priority", "IMPORTANT") == "IMPORTANT"]
    optional = [r for r in weighted_reqs if r.get("priority", "IMPORTANT") == "OPTIONAL"]

    return {
        "mission_id": mission_id,
        "metadata": {
            "name": metadata.get("name", "") if metadata else "",
            "description": metadata.get("description", "") if metadata else "",
            "category": metadata.get("category", "") if metadata else "",
        },
        "weighted_requirements": weighted_reqs,
        "priority_breakdown": {
            "critical": [r["product_id"] for r in critical],
            "important": [r["product_id"] for r in important],
            "optional": [r["product_id"] for r in optional],
        },
        "simulation_rules": rules,
        "parameters": parameters,
        "intent_count": len(intents),
        "synonym_count": len(synonyms),
        "relationship_count": len(requirements),
        "has_metadata": metadata is not None,
        "has_embedding": bool(metadata and metadata.get("embedding")),
    }
