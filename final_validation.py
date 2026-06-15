import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from engines.domains.mission_detection.service import MissionDetectionService
from engines.domains.mission_detection.schemas import MissionDetectionRequest

def run_validation():
    service = MissionDetectionService()

    queries = [
        {
            "text": "Need rice, atta and oil for the entire month",
            "expected_mission": "monthly_grocery_refill"
        },
        {
            "text": "Need groceries for my family of 4 this week",
            "expected_mission": "weekly_grocery_shopping"
        },
        {
            "text": "I am planning biryani for 20 guests under 8000",
            "expected_mission": "chicken_biryani",
            "expected_params": {
                "guest_count": 20,
                "budget": 8000
            }
        },
        {
            "text": "I am turning 20 tomorrow and inviting 15 friends",
            "expected_mission": "birthday_party"
        },
        {
            "text": "My exams start next week",
            "expected_mission": "exam_preparation_week"
        }
    ]

    all_passed = True

    for i, q in enumerate(queries, 1):
        text = q["text"]
        req = MissionDetectionRequest(text=text, user_id="test", session_id="test")
        
        try:
            res = service.detect(req)
        except Exception as e:
            print(f"Error on query '{text}': {e}")
            all_passed = False
            continue
            
        mission = res.detected_mission
        params = res.parameters
        
        passed = (mission == q["expected_mission"])
        if "expected_params" in q:
            for k, v in q["expected_params"].items():
                if params.get(k) != v:
                    passed = False
                    
        print(f"Test {i}: {text}")
        print(f"  Detected Mission: {mission} (Expected: {q['expected_mission']})")
        print(f"  Extracted Params: {params}")
        if passed:
            print("  Result: PASS\n")
        else:
            print("  Result: FAIL\n")
            all_passed = False

    if all_passed:
        print("FINAL VALIDATION: ALL PASSED")
    else:
        print("FINAL VALIDATION: SOME TESTS FAILED")

if __name__ == '__main__':
    run_validation()
