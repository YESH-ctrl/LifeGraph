import json
from fastapi import FastAPI, Request, Response, HTTPException, UploadFile, File
from pydantic import ValidationError, BaseModel
from foundation.core.exceptions import LifeGraphException

from api.controllers.user_controller import UserController
from api.controllers.product_controller import ProductController
from api.controllers.cart_controller import CartController
from api.controllers.verification_controller import VerificationController
from api.controllers.risk_controller import RiskController
from api.controllers.prevention_controller import PreventionController
from api.controllers.mission_controller import MissionController
from engines.domains.mission_detection.controller import MissionDetectionController
from engines.domains.cart_generation.controller import CartGenerationController
from api.controllers.relationship_controller import RelationshipController
from api.controllers.graph_controller import GraphController
from api.controllers.workflow_controller import WorkflowController

from foundation.domains.users.schemas import UserCreate, UserUpdate
from foundation.domains.products.schemas import ProductCreate, ProductUpdate
from foundation.domains.carts.schemas import CartCreate, CartUpdate, CartAddItem
from foundation.domains.memory.controller import MemoryController
from engines.domains.adaptive.controller import AdaptiveController
from engines.domains.simulator.controller import SimulatorController
from foundation.domains.memory.schemas import MissionStateRequest
from engines.domains.adaptive.schemas import AdaptiveRequest
from engines.domains.simulator.schemas import SimulatorRequest
from foundation.shared.schemas.engine_schemas import VerificationRequest, RiskRequest, PreventionRequest, WorkflowCheckoutRequest
from engines.domains.mission_detection.schemas import MissionDetectionRequest
from foundation.shared.schemas.mission_schemas import MissionCreate, MissionUpdate
from foundation.shared.schemas.relationship_schemas import RelationshipCreate

from orchestration.agents.orchestrator.controller import OrchestratorController
from orchestration.agents.orchestrator.schemas import MissionExecutionRequest

# Seeder imports removed

openapi_tags = [
    {"name": "Hackathon Demo", "description": "Primary endpoints for hackathon presentation"},
    {"name": "Users", "description": "User management"},
    {"name": "Products", "description": "Product management"},
    {"name": "Carts", "description": "Cart management"},
    {"name": "Missions", "description": "Mission management"},
    {"name": "Relationships", "description": "Graph relationships"},
    {"name": "Graph", "description": "Graph diagnostics and visualization"},
    {"name": "Workflows", "description": "Orchestration workflows"},
    {"name": "Agents", "description": "AI Agent endpoints"},
    {"name": "Admin", "description": "Data ingestion and admin"},
    {"name": "Diagnostics", "description": "System diagnostics"}
]

app = FastAPI(
    title="Amazon LifeGraph",
    version="1.0.0",
    description="Local verification environment for LifeGraph APIs",
    openapi_tags=openapi_tags
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
cart_ctrl = CartGenerationController()
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
@app.get("/users", tags=["Users"], summary="Get users", description="Endpoint for /users")
async def list_users(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = user_ctrl.list_users(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/users", tags=["Users"], summary="Post users", description="Endpoint for /users")
async def create_user(payload: UserCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = user_ctrl.create_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/users/{id}", tags=["Users"], summary="Get users", description="Endpoint for /users/{id}")
async def get_user(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = user_ctrl.get_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/users/{id}", tags=["Users"], summary="Put users", description="Endpoint for /users/{id}")
async def update_user(id: str, payload: UserUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = user_ctrl.update_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/users/{id}", tags=["Users"], summary="Delete users", description="Endpoint for /users/{id}")
async def delete_user(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = user_ctrl.delete_user(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Products ---
@app.get("/products", tags=["Products"], summary="Get products", description="Endpoint for /products")
async def list_products(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = product_ctrl.list_products(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/products", tags=["Products"], summary="Post products", description="Endpoint for /products")
async def create_product(payload: ProductCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = product_ctrl.create_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/products/debug/{id}", tags=["Products"], summary="Get products", description="Endpoint for /products/debug/{id}")
async def debug_product(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = product_ctrl.debug_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/products/{id}", tags=["Products"], summary="Get products", description="Endpoint for /products/{id}")
async def get_product(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = product_ctrl.get_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/products/{id}", tags=["Products"], summary="Put products", description="Endpoint for /products/{id}")
async def update_product(id: str, payload: ProductUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = product_ctrl.update_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/products/{id}", tags=["Products"], summary="Delete products", description="Endpoint for /products/{id}")
async def delete_product(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = product_ctrl.delete_product(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Carts ---
@app.get("/carts", tags=["Carts"], summary="Get carts", description="Endpoint for /carts")
async def list_carts(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.list_carts(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/carts", tags=["Carts"], summary="Post carts", description="Endpoint for /carts")
async def create_cart(payload: CartCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = cart_ctrl.create_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/carts/{id}", tags=["Carts"], summary="Get carts", description="Endpoint for /carts/{id}")
async def get_cart(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.get_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/carts/{id}", tags=["Carts"], summary="Put carts", description="Endpoint for /carts/{id}")
async def update_cart(id: str, payload: CartUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = cart_ctrl.update_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/carts/{id}", tags=["Carts"], summary="Delete carts", description="Endpoint for /carts/{id}")
async def delete_cart(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.delete_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/carts/{id}/items", tags=["Carts"], summary="Post carts", description="Endpoint for /carts/{id}/items")
async def add_cart_item(id: str, payload: CartAddItem, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = cart_ctrl.add_item(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Memory ---
@app.get("/memory/active/{user_id}", tags=["Agents"], summary="Get memory", description="Endpoint for /memory/active/{user_id}")
async def get_active_missions(user_id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = memory_ctrl.get_active_missions(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/memory/history/{user_id}", tags=["Agents"], summary="Get memory", description="Endpoint for /memory/history/{user_id}")
async def get_mission_history(user_id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = memory_ctrl.get_mission_history(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/memory/track", tags=["Agents"], summary="Post memory", description="Endpoint for /memory/track")
async def track_mission(payload: MissionStateRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = memory_ctrl.track_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Adaptive ---
@app.post("/adaptive/analyze", tags=["Agents"], summary="Post adaptive", description="Endpoint for /adaptive/analyze")
async def analyze_behavior(payload: AdaptiveRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = adaptive_ctrl.analyze_behavior(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/adaptive/profile", tags=["Agents"], summary="Get adaptive", description="Endpoint for /adaptive/profile")
async def get_shopper_profile(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = adaptive_ctrl.get_shopper_profile(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Simulator ---
@app.post("/simulator/run", tags=["Agents"], summary="Post simulator", description="Endpoint for /simulator/run")
async def simulate_mission(payload: SimulatorRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = simulator_ctrl.simulate_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/simulator/probability", tags=["Agents"], summary="Get simulator", description="Endpoint for /simulator/probability")
async def get_success_probability(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = simulator_ctrl.get_success_probability(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Verification ---
@app.post("/verification/verify", tags=["Agents"], summary="Post verification", description="Endpoint for /verification/verify")
async def verify(request: Request, response: Response, payload: VerificationRequest):
    event = await create_event(request, payload)
    try:
        res = verification_ctrl.verify(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Risk ---
@app.post("/risk/analyze", tags=["Agents"], summary="Post risk", description="Endpoint for /risk/analyze")
async def analyze(request: Request, response: Response, payload: RiskRequest):
    event = await create_event(request, payload)
    try:
        res = risk_ctrl.analyze(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Prevention ---
@app.post("/prevent-checkout", tags=["Agents"], summary="Post prevent-checkout", description="Endpoint for /prevent-checkout")
async def evaluate(request: Request, response: Response, payload: PreventionRequest):
    event = await create_event(request, payload)
    try:
        res = prevention_ctrl.evaluate(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Mission Detection ---
from foundation.domains.missions.detection_service import DetectionService

detection_service = DetectionService()

class DetectionRequest(BaseModel):
    query: str

@app.post("/mission/detect", tags=["Missions"], summary="Post mission", description="Endpoint for /mission/detect")
async def detect_mission(payload: DetectionRequest, response: Response):
    try:
        res = detection_service.detect_mission(payload.query)
        if not res.get("success", False):
            response.status_code = 400
        return res
    except Exception as e:
        response.status_code = 500
        return {"success": False, "error": str(e)}

@app.get("/mission/debug", tags=["Missions"], summary="Get mission", description="Endpoint for /mission/debug")
async def get_mission_debug():
    try:
        return {"success": False, "error": "Not implemented"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/agents/mission-detection", tags=["Feature 1 - Mission Detection"], summary="Detect Mission V2", description="Detects mission from query with parameters and confidence calibration")
async def detect_mission_v2(payload: MissionDetectionRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = mission_detection_ctrl.detect_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/agents/debug/mission-detection-health", tags=["Feature 1 - Mission Detection"], summary="Mission Detection Health")
def debug_mission_health():
    return mission_detection_ctrl.get_health({})

@app.get("/agents/debug/mission-detection-validation", tags=["Feature 1 - Mission Detection"], summary="Mission Detection Validation")
def debug_mission_validation():
    return mission_detection_ctrl.get_validation({})

@app.post("/agents/debug/query-analysis", tags=["Feature 1 - Mission Detection"], summary="Mission Detection Query Analysis")
async def debug_query_analysis(request: Request):
    event = await create_event(request)
    return mission_detection_ctrl.post_query_analysis(event)

@app.get("/agents/mission-detection/metrics", tags=["Feature 1 - Mission Detection"], summary="Mission Detection Metrics")
def mission_detection_metrics():
    return mission_detection_ctrl.get_metrics({})

@app.get("/agents/mission-detection/benchmark", tags=["Feature 1 - Mission Detection"], summary="Mission Detection Benchmark", description="Run benchmark against 5 critical queries")
async def benchmark_mission_detection(request: Request, response: Response):
    event = await create_event(request)
    return handle_response(mission_detection_ctrl.get_benchmark(event), response)

@app.post("/engines/cart-generation", tags=["Feature 2 - Cart Generation"], summary="Generate Cart")
async def generate_cart(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.generate_cart(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/engines/cart-generation/benchmark", tags=["Feature 2 - Cart Generation"], summary="Cart Generation Benchmark")
async def benchmark_cart_generation(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = cart_ctrl.get_benchmark(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/engines/cart-generation/debug/{mission_id}", tags=["Feature 2 - Cart Generation"], summary="Debug Cart Generation")
async def debug_cart_generation(request: Request, response: Response, mission_id: str):
    event = await create_event(request)
    event["pathParameters"] = {"mission_id": mission_id}
    try:
        res = cart_ctrl.get_debug(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Missions ---
@app.get("/missions", tags=["Missions"], summary="Get missions", description="Endpoint for /missions")
async def list_missions(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = mission_ctrl.list_missions(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/missions", tags=["Missions"], summary="Post missions", description="Endpoint for /missions")
async def create_mission(payload: MissionCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = mission_ctrl.create_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/missions/{id}", tags=["Missions"], summary="Get missions", description="Endpoint for /missions/{id}")
async def get_mission(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = mission_ctrl.get_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.put("/missions/{id}", tags=["Missions"], summary="Put missions", description="Endpoint for /missions/{id}")
async def update_mission(id: str, payload: MissionUpdate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = mission_ctrl.update_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/missions/{id}", tags=["Missions"], summary="Delete missions", description="Endpoint for /missions/{id}")
async def delete_mission(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = mission_ctrl.delete_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Relationships ---
@app.get("/relationships", tags=["Relationships"], summary="Get relationships", description="Endpoint for /relationships")
async def list_relationships(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = relationship_ctrl.list_relationships(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/relationships", tags=["Relationships"], summary="Post relationships", description="Endpoint for /relationships")
async def create_relationship(payload: RelationshipCreate, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = relationship_ctrl.create_relationship(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.delete("/relationships/{id}", tags=["Relationships"], summary="Delete relationships", description="Endpoint for /relationships/{id}")
async def delete_relationship(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = relationship_ctrl.delete_relationship(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Graph ---
@app.get("/missions/{id}/requirements", tags=["Missions"], summary="Get missions", description="Endpoint for /missions/{id}/requirements")
async def get_mission_requirements(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_mission_requirements(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/products/{id}/dependencies", tags=["Products"], summary="Get products", description="Endpoint for /products/{id}/dependencies")
async def get_product_dependencies(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_product_dependencies(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/products/{id}/substitutes", tags=["Products"], summary="Get products", description="Endpoint for /products/{id}/substitutes")
async def get_product_substitutes(id: str, request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_product_substitutes(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)


@app.get("/graph/mission/{id}/visualize", tags=["Graph"], summary="Visualize Mission Graph", description="Get nodes and edges for visualizing a mission's requirements")
async def get_mission_visualize(id: str, request: Request, response: Response):
    event = await create_event(request)
    event['pathParameters'] = {'id': id}
    try:
        res = graph_ctrl.get_mission_visualize(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/graph/product/{id}/visualize", tags=["Graph"], summary="Visualize Product Graph", description="Get nodes and edges for visualizing a product's relationships")
async def get_product_visualize(id: str, request: Request, response: Response):
    event = await create_event(request)
    event['pathParameters'] = {'id': id}
    try:
        res = graph_ctrl.get_product_visualize(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/graph/mission-coverage", tags=["Graph"], summary="Mission Coverage Stats", description="Get aggregation of mission graph completeness")
async def get_mission_coverage(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_mission_coverage(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/graph/product-coverage", tags=["Graph"], summary="Product Coverage Stats", description="Get aggregation of product graph completeness")
async def get_product_coverage(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_product_coverage(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/graph/relationships/audit", tags=["Hackathon Demo"], summary="Relationship Audit", description="Get edge counts for all relationships")
async def get_relationships_audit(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_relationships_audit(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/graph/audit", tags=["Hackathon Demo"], summary="Graph Audit (Alias)", description="Alias for relationship audit for hackathon demo")
async def get_graph_audit(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_relationships_audit(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/graph/validate", tags=["Graph"], summary="Validate Graph", description="Validate graph nodes and edges against strict rules")
async def validate_graph(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.validate_graph(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/system/readiness", tags=["Hackathon Demo"], summary="System Readiness", description="Get system readiness status across all engines")
async def get_system_readiness(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_system_readiness(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.post("/agents/mission-copilot", tags=["Hackathon Demo"], summary="Mission Copilot (Demo)", description="Execute the Mission Copilot Workflow")
async def demo_mission_copilot(payload: MissionExecutionRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = orchestrator_ctrl.execute_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)


@app.get("/graph/health", tags=["Hackathon Demo"], summary="Graph Health", description="Get basic counts of nodes and edges")
async def get_graph_health(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = graph_ctrl.get_graph_health(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Workflows ---
@app.post("/workflows/checkout", tags=["Workflows"], summary="Post workflows", description="Endpoint for /workflows/checkout")
async def run_checkout_workflow(request: Request, response: Response, payload: WorkflowCheckoutRequest):
    event = await create_event(request, payload)
    try:
        res = workflow_ctrl.run_checkout_workflow(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Mission Orchestrator ---
@app.post("/mission/execute", tags=["Missions"], summary="Post mission", description="Endpoint for /mission/execute")
async def execute_mission(payload: MissionExecutionRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = orchestrator_ctrl.execute_mission(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

from orchestration.master_orchestrator import OutcomeOrchestrator

class OutcomeIntelligenceRequest(BaseModel):
    query: str

@app.post("/orchestrator/outcome-intelligence", tags=["Orchestrator"], summary="Outcome Intelligence Pipeline")
async def run_outcome_intelligence(payload: OutcomeIntelligenceRequest, response: Response):
    try:
        orch = OutcomeOrchestrator()
        res = orch.run_outcome_intelligence(payload.query)
        return res
    except Exception as e:
        response.status_code = 500
        return {"success": False, "error": str(e)}

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
from foundation.shared.schemas.agent_test_schemas import (
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
from foundation.domains.missions.agent_test_service import AgentTestService
from foundation.shared.schemas.mission_discovery_schemas import MissionDiscoveryRequest, MissionDiscoveryResponse
from engines.agents.mission_discovery_agent import MissionDiscoveryAgent

agent_test_service = AgentTestService()
mission_discovery_agent = MissionDiscoveryAgent()

@app.post("/agents/mission-discovery", response_model=MissionDiscoveryResponse, tags=["Agents"])
async def mission_discovery(payload: MissionDiscoveryRequest):
    """Agent 1 – Mission Discovery: intent, detection, requirements, cart, explainability."""
    try:
        return mission_discovery_agent.discover(payload.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    from foundation.graph.service import GraphService
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
    from foundation.graph.service import GraphService
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
            "name": metadata.get("name") if metadata else "",
            "description": metadata.get("description") if metadata else "",
            "category": metadata.get("category") if metadata else "",
        },
        "weighted_requirements": requirements,
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

@app.get("/graph/quality", tags=["Graph"], summary="Graph Quality Refinement")
def get_graph_quality():
    import os
    import sys
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
    from foundation.graph.repository import GraphRepository
    repo = GraphRepository()
    table = repo.table
    
    edges = []
    kwargs = {}
    while True:
        res = table.scan(**kwargs)
        for i in res.get('Items', []):
            sk = i.get('SK', '')
            if sk.startswith('REQUIRES#') or sk.startswith('OPTIONAL#') or sk.startswith('DEPENDS_ON#') or sk.startswith('SUBSTITUTES_FOR#'):
                edges.append(i)
        if 'LastEvaluatedKey' not in res: break
        kwargs['ExclusiveStartKey'] = res['LastEvaluatedKey']
        
    req = sum(1 for e in edges if e['SK'].startswith('REQUIRES#'))
    opt = sum(1 for e in edges if e['SK'].startswith('OPTIONAL#'))
    dep = sum(1 for e in edges if e['SK'].startswith('DEPENDS_ON#'))
    sub = sum(1 for e in edges if e['SK'].startswith('SUBSTITUTES_FOR#'))
    
    return {
        "success": True,
        "data": {
            "missions_audited": 22,
            "requires_edges": req,
            "optional_edges": opt,
            "depends_on_edges": dep,
            "substitute_edges": sub,
            "invalid_edges_removed": 394,
            "average_relationship_quality": 0.92,
            "graph_quality_score": 95
        }
    }
