import json
from fastapi import FastAPI, Request, Response
from pydantic import ValidationError, BaseModel
from core.exceptions import LifeGraphException

from domains.users.controller import UserController
from domains.products.controller import ProductController
from domains.carts.controller import CartController
from domains.verification.controller import VerificationController
from domains.risk.controller import RiskController
from domains.prevention.controller import PreventionController
from domains.verification.schemas import VerificationRequest
from domains.risk.schemas import RiskRequest
from domains.prevention.schemas import PreventionRequest

from domains.users.schemas import UserCreate, UserUpdate
from domains.products.schemas import ProductCreate, ProductUpdate
from domains.carts.schemas import CartCreate, CartUpdate, CartAddItem
from domains.memory.controller import MemoryController
from domains.adaptive.controller import AdaptiveController
from domains.simulator.controller import SimulatorController
from domains.memory.schemas import MissionStateRequest
from domains.adaptive.schemas import AdaptiveRequest
from domains.simulator.schemas import SimulatorRequest

app = FastAPI(
    title="Amazon LifeGraph",
    version="1.0.0",
    description="Local verification environment for LifeGraph APIs"
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
@app.get("/memory/active")
async def get_active_missions(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = memory_ctrl.get_active_missions(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/memory/history")
async def get_mission_history(request: Request, response: Response):
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
        res = adaptive_ctrl.handle(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/adaptive/profile")
async def get_shopper_profile(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = adaptive_ctrl.handle(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Simulator ---
@app.post("/simulator/run")
async def simulate_mission(payload: SimulatorRequest, request: Request, response: Response):
    event = await create_event(request, payload)
    try:
        res = simulator_ctrl.run(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

@app.get("/simulator/probability")
async def get_success_probability(request: Request, response: Response):
    event = await create_event(request)
    try:
        res = simulator_ctrl.run(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Verification ---
@app.post("/verification/verify")
async def verify(request: Request, response: Response, payload: VerificationRequest):
    event = await create_event(request)
    try:
        res = verification_ctrl.verify(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Risk ---
@app.post("/risk/analyze")
async def analyze(request: Request, response: Response, payload: RiskRequest):
    event = await create_event(request)
    try:
        res = risk_ctrl.analyze(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

# --- Prevention ---
@app.post("/prevent-checkout")
async def evaluate(request: Request, response: Response, payload: PreventionRequest):
    event = await create_event(request)
    try:
        res = prevention_ctrl.evaluate(event)
        return handle_controller_response(response, res)
    except Exception as e:
        return handle_exception(e, response)

