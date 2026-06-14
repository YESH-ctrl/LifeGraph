import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engines.domains.mission_detection.service import MissionDetectionService
from engines.domains.mission_detection.schemas import MissionDetectionRequest

ambiguous_prompts = [
    "I am hungry",
    "Feeling low today",
    "Need help",
    "Want to buy something",
    "What should I buy",
    "Going out",
    "Need something",
    "bored",
    "i am sad",
    "feeling down",
    "want to eat",
    "what to do",
    "i need to eat",
    "starving",
    "hungry",
    "feel like eating",
    "just need a snack",
    "im so hungry",
    "need food",
    "buy me something",
    "want a gift",
    "want to order",
    "help me choose",
    "what to eat",
    "what to buy",
    "feeling tired",
    "i am thirsty",
    "so tired",
    "going for a walk",
    "walking outside",
    "bored at home",
    "not sure what to get",
    "recommend me something",
    "i don't know",
    "anything is fine",
    "i want something new",
    "can you suggest something",
    "random items",
    "just browsing",
    "i need stuff",
    "getting things",
    "buying items",
    "i am happy",
    "feeling good",
    "having fun",
    "chilling",
    "relaxing",
    "doing nothing",
    "wasting time",
    "don't know what I want"
]

def run_benchmark():
    service = MissionDetectionService()
    
    passed = 0
    failed = []
    
    print("Running Ambiguity Benchmark...")
    
    for prompt in ambiguous_prompts:
        req = MissionDetectionRequest(text=prompt)
        res = service.detect(req)
        
        if res.detected_mission == "UNKNOWN":
            passed += 1
        else:
            failed.append({
                "prompt": prompt,
                "predicted": res.detected_mission,
                "confidence": res.confidence
            })
            
    print("="*40)
    print(f"Passed: {passed}/{len(ambiguous_prompts)}")
    print("="*40)
    
    if failed:
        print("FAILURES:")
        for f in failed:
            print(f"Prompt: '{f['prompt']}' -> Predicted: {f['predicted']} (Conf: {f['confidence']:.2f})")
    else:
        print("All ambiguous prompts successfully returned UNKNOWN!")

    # Now verify the explicit positive examples
    print("\nVerifying specific positive examples...")
    positives = {
        "Want to cook biryani tonight": "CHICKEN_BIRYANI",
        "Going camping this weekend": "CAMPING_TRIP",
        "Movie night with friends": "MOVIE_NIGHT"
    }
    for p, expected in positives.items():
        req = MissionDetectionRequest(text=p)
        res = service.detect(req)
        if res.detected_mission == expected:
            print(f"SUCCESS: '{p}' -> {expected}")
        else:
            print(f"FAILURE: '{p}' -> Expected {expected}, got {res.detected_mission}")

if __name__ == "__main__":
    run_benchmark()
