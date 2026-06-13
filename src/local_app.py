import json
from fastapi import FastAPI, Request, Response
from pydantic import ValidationError, BaseModel
from core.exceptions import LifeGraphException

from domains.users.controller import UserController
from domains.products.controller import ProductController
from domains.carts.controller import CartController
from domains.missions.controller import MissionController
from domains.relationships.controller import RelationshipController
from domains.graph.controller import GraphController

from domains.users.schemas import UserCreate, UserUpdate
from domains.products.schemas import ProductCreate, ProductUpdate
from domains.carts.schemas import CartCreate, CartUpdate, CartAddItem
from domains.missions.schemas import MissionCreate, MissionUpdate
from domains.relationships.schemas import RelationshipCreate

app = FastAPI(
    title="Amazon LifeGraph",
    version="1.0.0",
    description="Local verification environment for LifeGraph APIs"
)

user_ctrl = UserController()
product_ctrl = ProductController()
cart_ctrl = CartController()
mission_ctrl = MissionController()
relationship_ctrl = RelationshipController()
graph_ctrl = GraphController()

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
