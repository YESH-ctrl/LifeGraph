import json
from agents.mission_agent import MissionAgent
from shared.schemas.mission_schemas import MissionCreate, MissionUpdate, MissionResponse

class MissionController:
    def __init__(self):
        self.agent = MissionAgent()

    def create_mission(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = MissionCreate(**body)
        mission = self.agent.execute("create", schema)
        response = MissionResponse(
            mission_id=mission.mission_id, 
            name=mission.name, 
            description=mission.description, 
            category=mission.category
        )
        return {
            "statusCode": 201,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def get_mission(self, event: dict) -> dict:
        mission_id = event['pathParameters']['id']
        mission = self.agent.execute("get", mission_id)
        response = MissionResponse(
            mission_id=mission.mission_id, 
            name=mission.name, 
            description=mission.description, 
            category=mission.category
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def update_mission(self, event: dict) -> dict:
        mission_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        schema = MissionUpdate(**body)
        mission = self.agent.execute("update", {"mission_id": mission_id, "data": schema})
        response = MissionResponse(
            mission_id=mission.mission_id, 
            name=mission.name, 
            description=mission.description, 
            category=mission.category
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response.model_dump()})
        }

    def delete_mission(self, event: dict) -> dict:
        mission_id = event['pathParameters']['id']
        self.agent.execute("delete", mission_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": {}})
        }

    def list_missions(self, event: dict) -> dict:
        missions = self.agent.execute("list", None)
        response = [
            MissionResponse(
                mission_id=m.mission_id, 
                name=m.name, 
                description=m.description, 
                category=m.category
            ).model_dump()
            for m in missions
        ]
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": response})
        }
