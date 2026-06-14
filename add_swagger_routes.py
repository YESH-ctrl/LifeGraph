import os
import re

file_path = r"c:\Users\yeswa\Desktop\LifeGraphBackend\src\local_app.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update FastAPI initialization
openapi_tags_str = """
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
"""
content = re.sub(
    r'app = FastAPI\([\s\S]*?description=".*?"\n\)',
    openapi_tags_str.strip(),
    content
)

# 2. Inject basic tags to endpoints that lack them. 
# We'll map URL prefixes to tags.
tag_mapping = {
    "/users": "Users",
    "/products": "Products",
    "/carts": "Carts",
    "/missions": "Missions",
    "/mission/": "Missions", # will override specific ones later if needed
    "/relationships": "Relationships",
    "/graph": "Graph",
    "/memory": "Agents",
    "/adaptive": "Agents",
    "/simulator": "Agents",
    "/verification": "Agents",
    "/risk": "Agents",
    "/prevent-checkout": "Agents",
    "/workflows": "Workflows"
}

def add_tags(match):
    full_decorator = match.group(0)
    if "tags=" in full_decorator:
        return full_decorator # already tagged
    
    url = match.group(2)
    method = match.group(1)
    
    tag = "Diagnostics"
    for prefix, t in tag_mapping.items():
        if url.startswith(prefix):
            tag = t
            break
            
    # Add summary and description and tags
    summary = f"{method.capitalize()} {url.split('/')[1] if len(url.split('/'))>1 else 'resource'}"
    desc = f"Endpoint for {url}"
    
    new_decorator = f'@app.{method}("{url}", tags=["{tag}"], summary="{summary}", description="{desc}")'
    return new_decorator

# Regex to find @app.get("/something")
content = re.sub(r'@app\.(get|post|put|delete)\("([^"]+)"\)', add_tags, content)

# 3. Add new Graph API endpoints under the # --- Graph --- section
new_graph_endpoints = """
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

"""

# Insert new endpoints into the # --- Graph --- section, replacing the get_graph_health location slightly
content = content.replace(
    "@app.get(\"/graph/health\"",
    new_graph_endpoints + "\n@app.get(\"/graph/health\", tags=[\"Hackathon Demo\"], summary=\"Graph Health\", description=\"Get basic counts of nodes and edges\")"
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated local_app.py successfully.")
