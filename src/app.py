import json
import logging
import re
import os
from pydantic import ValidationError
from core.exceptions import LifeGraphException

from domains.users.controller import UserController
from domains.products.controller import ProductController
from domains.carts.controller import CartController
from domains.verification.controller import VerificationController
from domains.risk.controller import RiskController
from domains.prevention.controller import PreventionController
from domains.missions.controller import MissionController
from domains.relationships.controller import RelationshipController
from domains.graph.controller import GraphController
from domains.memory.controller import MemoryController
from domains.adaptive.controller import AdaptiveController
from domains.simulator.controller import SimulatorController
from domains.verification.controller import VerificationController
from domains.risk.controller import RiskController
from domains.prevention.controller import PreventionController
from api.controllers.mission_controller import MissionController
from api.controllers.relationship_controller import RelationshipController
from api.controllers.graph_controller import GraphController
from api.controllers.workflow_controller import WorkflowController
from agents.orchestrator.controller import OrchestratorController

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
relationship_ctrl = RelationshipController()
graph_ctrl = GraphController()
workflow_ctrl = WorkflowController()
orchestrator_ctrl = OrchestratorController()

def handler(event, context):
    logger.info(f"Received event: {event}")
    
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    
    try:
        # Swagger UI Routes
        if path == '/docs' and method == 'GET':
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="utf-8" />
              <meta name="viewport" content="width=device-width, initial-scale=1" />
              <title>SwaggerUI - LifeGraph</title>
              <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
            </head>
            <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" crossorigin></script>
            <script>
              window.onload = () => {
                window.ui = SwaggerUIBundle({
                  url: '/Prod/docs/openapi.yaml',
                  dom_id: '#swagger-ui',
                });
              };
            </script>
            </body>
            </html>
            """
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": html
            }
            
        elif path == '/docs/openapi.yaml' and method == 'GET':
            try:
                yaml_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'openapi.yaml')
                with open(yaml_path, 'r') as f:
                    content = f.read()
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/yaml"},
                    "body": content
                }
            except Exception as e:
                logger.error(f"Error reading openapi.yaml: {e}")
                return {
                    "statusCode": 500,
                    "body": "Could not load OpenAPI spec"
                }

        # User Routes
        elif path == '/users' and method == 'GET':
            return user_ctrl.list_users(event)
        elif path == '/users' and method == 'POST':
            return user_ctrl.create_user(event)
        elif path.startswith('/users/') and method == 'GET':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return user_ctrl.get_user(event)
        elif path.startswith('/users/') and method == 'PUT':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return user_ctrl.update_user(event)
        elif path.startswith('/users/') and method == 'DELETE':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return user_ctrl.delete_user(event)
            
        # Product Routes
        elif path == '/products' and method == 'GET':
            return product_ctrl.list_products(event)
        elif path == '/products' and method == 'POST':
            return product_ctrl.create_product(event)
        elif path.startswith('/products/') and method == 'GET':
            if path.endswith('/dependencies'):
                event['pathParameters'] = {'id': path.split('/')[-2]}
                return graph_ctrl.get_product_dependencies(event)
            if path.endswith('/substitutes'):
                event['pathParameters'] = {'id': path.split('/')[-2]}
                return graph_ctrl.get_product_substitutes(event)
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return product_ctrl.get_product(event)
        elif path.startswith('/products/') and method == 'PUT':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return product_ctrl.update_product(event)
        elif path.startswith('/products/') and method == 'DELETE':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return product_ctrl.delete_product(event)
            
        # Cart Routes
        elif path == '/carts' and method == 'GET':
            return cart_ctrl.list_carts(event)
        elif path == '/carts' and method == 'POST':
            return cart_ctrl.create_cart(event)
        elif re.match(r'^/carts/[^/]+$', path) and method == 'GET':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return cart_ctrl.get_cart(event)
        elif re.match(r'^/carts/[^/]+$', path) and method == 'PUT':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return cart_ctrl.update_cart(event)
        elif re.match(r'^/carts/[^/]+$', path) and method == 'DELETE':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return cart_ctrl.delete_cart(event)
        elif re.match(r'^/carts/[^/]+/items$', path) and method == 'POST':
            event['pathParameters'] = {'id': path.split('/')[-2]}
            return cart_ctrl.add_item(event)
            
        # Memory Routes
        elif path.startswith('/memory/active/') and method == 'GET':
            event['pathParameters'] = {'user_id': path.split('/')[-1]}
            return memory_ctrl.get_active_missions(event)
        elif path.startswith('/memory/history/') and method == 'GET':
            event['pathParameters'] = {'user_id': path.split('/')[-1]}
            return memory_ctrl.get_mission_history(event)
        elif path == '/memory/track' and method == 'POST':
            return memory_ctrl.track_mission(event)

        # Adaptive Routes
        elif path == '/adaptive/analyze' and method == 'POST':
            return adaptive_ctrl.analyze_behavior(event)
        elif path == '/adaptive/profile' and method == 'GET':
            return adaptive_ctrl.get_shopper_profile(event)

        # Simulator Routes
        elif path == '/simulator/run' and method == 'POST':
            return simulator_ctrl.simulate_mission(event)
        elif path == '/simulator/probability' and method == 'GET':
            return simulator_ctrl.get_success_probability(event)

        # Verification Routes
        elif path == '/verification/verify' and method == 'POST':
            return verification_ctrl.verify(event)
            
        # Risk Routes
        elif path == '/risk/analyze' and method == 'POST':
            return risk_ctrl.analyze(event)
            
        # Prevention Routes
        elif path == '/prevent-checkout' and method == 'POST':
            return prevention_ctrl.evaluate(event)

        # Mission Routes
        elif path == '/missions' and method == 'GET':
            return mission_ctrl.list_missions(event)
        elif path == '/missions' and method == 'POST':
            return mission_ctrl.create_mission(event)
        elif path.startswith('/missions/') and method == 'GET':
            if path.endswith('/requirements'):
                event['pathParameters'] = {'id': path.split('/')[-2]}
                return graph_ctrl.get_mission_requirements(event)
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return mission_ctrl.get_mission(event)
        elif path.startswith('/missions/') and method == 'PUT':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return mission_ctrl.update_mission(event)
        elif path.startswith('/missions/') and method == 'DELETE':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return mission_ctrl.delete_mission(event)

        # Relationship Routes
        elif path == '/relationships' and method == 'GET':
            return relationship_ctrl.list_relationships(event)
        elif path == '/relationships' and method == 'POST':
            return relationship_ctrl.create_relationship(event)
        elif path.startswith('/relationships/') and method == 'DELETE':
            event['pathParameters'] = {'id': path.split('/')[-1]}
            return relationship_ctrl.delete_relationship(event)

        # Workflow Routes
        elif path == '/workflows/checkout' and method == 'POST':
            return workflow_ctrl.run_checkout_workflow(event)

        # Mission Orchestrator Routes
        elif path == '/mission/execute' and method == 'POST':
            return orchestrator_ctrl.execute_mission(event)
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"success": False, "error": {"code": "NOT_FOUND", "message": "Route not found"}})
            }
            
    except ValidationError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload",
                    "details": e.errors()
                }
            })
        }
    except LifeGraphException as e:
        return {
            "statusCode": e.status_code,
            "body": json.dumps({
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message
                }
            })
        }
    except Exception as e:
        logger.error(f"Internal error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            })
        }
