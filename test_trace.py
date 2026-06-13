import os
import sys

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from domains.memory.controller import MemoryController
from pydantic import BaseModel

class MockRequest(BaseModel):
    user_id: str
    mission_id: str
    mission_name: str
    status: str

event = {
    'body': MockRequest(user_id="USER123", mission_id="BIRTHDAY", mission_name="Birthday Party", status="ACTIVE").model_dump_json()
}

try:
    ctrl = MemoryController()
    res = ctrl.track_mission(event)
    print("SUCCESS:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
