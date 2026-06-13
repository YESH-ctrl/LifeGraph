import json
from domains.missions.service import MissionService
from domains.missions.schemas import MissionCreate, MissionUpdate, MissionResponse

class MissionController:
    def __init__(self):
        self.service = MissionService()

    def create_mission(self, event: dict) -> dict:
        body = json.loads(event.get('body', '{}'))
        schema = MissionCreate(**body)
        mission = self.service.create_mission(schema)
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
        mission = self.service.get_mission(mission_id)
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
        mission = self.service.update_mission(mission_id, schema)
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
        self.service.delete_mission(mission_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"success": True, "data": {}})
        }

    def list_missions(self, event: dict) -> dict:
        missions = self.service.list_missions()
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
