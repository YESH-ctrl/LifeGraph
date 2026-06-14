import sys
import os
import json
from collections import defaultdict

# Add src to path to import domains
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engines.domains.mission_detection.service import MissionDetectionService
from engines.domains.mission_detection.schemas import MissionDetectionRequest

test_suite = {
    "CHICKEN_BIRYANI": [
        "I want to cook biryani tonight",
        "need some basmati and chicken for a spicy meal",
        "family dinner with indian flavored rice",
        "making a big pot of chicken and rice with spices",
        "buying ingredients for a biryani recipe"
    ],
    "PASTA_DINNER": [
        "Italian night with spaghetti",
        "craving some garlic bread and penne",
        "need tomatoes and noodles for dinner",
        "making a creamy fettuccine for the kids",
        "going to cook a large bowl of macaroni"
    ],
    "BREAKFAST": [
        "need to buy eggs, bacon and some bread",
        "making a big morning feast",
        "getting ready to cook some pancakes",
        "buying coffee and cereal",
        "need fresh orange juice and bagels"
    ],
    "WEEKLY_GROCERIES": [
        "I need groceries for the week",
        "going to the supermarket for my regular shopping",
        "stocking up on household essentials",
        "buying veggies and staples for the next seven days",
        "my fridge is empty and i need to restock everything"
    ],
    "HOUSE_PARTY": [
        "I'm hosting a house party tonight",
        "having a bunch of people over for drinks",
        "need solo cups, ice, and beer",
        "throwing a big gathering at my place",
        "getting snacks for the guests coming tonight"
    ],
    "MOVIE_NIGHT": [
        "Movie night with friends",
        "watching a horror film on the couch",
        "getting popcorn and soda for the screen",
        "renting a movie and need some treats",
        "cinema vibes at home tonight"
    ],
    "ROAD_TRIP": [
        "Driving out of state for the weekend",
        "need car snacks and energy drinks",
        "hitting the road for a long journey",
        "packing the trunk for a drive to the mountains",
        "long trip ahead, need provisions"
    ],
    "CAMPING_TRIP": [
        "Going camping this weekend",
        "need bug spray and a sleeping bag",
        "pitching a tent in the forest",
        "getting ready for a campfire and s'mores",
        "outdoor survival trip"
    ],
    "SICK_DAY_RECOVERY": [
        "I caught a nasty flu",
        "need cough syrup and chicken soup",
        "staying home with a fever today",
        "buying vitamin c and tissues",
        "feeling terrible, need remedies"
    ],
    "BABY_CARE": [
        "running out of formula and wipes",
        "need to buy newborn supplies",
        "getting things for my toddler's nursery",
        "shopping for baby powder and lotion",
        "picking up diapers for the little one"
    ],
    "PET_CARE": [
        "buying kibble for my golden retriever",
        "need cat treats and a scratching post",
        "picking up supplies for the new puppy",
        "restocking fish food",
        "getting doggie bags and chew toys"
    ],
    "WORK_FROM_HOME": [
        "need a new webcam and desk snacks",
        "preparing for back to back zoom meetings",
        "home office setup needs an upgrade",
        "working from my living room today",
        "telecommuting and need coffee"
    ],
    "GYM_JOURNEY": [
        "starting my weight loss program",
        "need pre-workout and protein bars",
        "going to lift heavy weights today",
        "getting fitness gear and supplements",
        "training for a marathon"
    ],
    "HOUSEWARMING": [
        "visiting my sister's new apartment",
        "they just bought a house, need a gift",
        "going to a moving-in celebration",
        "buying a present for the new homeowners",
        "welcome to the neighborhood party"
    ],
    "BIRTHDAY_PARTY": [
        "my sister is turning 25",
        "need to buy a cake with candles",
        "getting balloons and a present",
        "surprise party for a friend getting older",
        "buying a happy bday card"
    ]
}

def run_benchmark():
    service = MissionDetectionService()
    
    total_prompts = 0
    correct_predictions = 0
    
    mission_accuracy = defaultdict(lambda: {"total": 0, "correct": 0})
    confusion_matrix = defaultdict(lambda: defaultdict(int))
    failures = []

    print("Running Mission Detection Benchmark...\n")

    for true_mission, prompts in test_suite.items():
        for prompt in prompts:
            total_prompts += 1
            mission_accuracy[true_mission]["total"] += 1
            
            request = MissionDetectionRequest(text=prompt)
            response = service.detect(request)
            predicted_mission = response.detected_mission
            
            confusion_matrix[true_mission][predicted_mission] += 1
            
            if predicted_mission == true_mission:
                correct_predictions += 1
                mission_accuracy[true_mission]["correct"] += 1
            else:
                failures.append({
                    "prompt": prompt,
                    "true_mission": true_mission,
                    "predicted_mission": predicted_mission,
                    "confidence": response.confidence
                })

    overall_accuracy = (correct_predictions / total_prompts) * 100
    
    print("="*50)
    print(f"Overall Accuracy: {overall_accuracy:.2f}% ({correct_predictions}/{total_prompts})")
    print("="*50)
    print("\nPer Mission Accuracy:")
    for mission, stats in mission_accuracy.items():
        acc = (stats["correct"] / stats["total"]) * 100
        print(f"  {mission}: {acc:.2f}% ({stats['correct']}/{stats['total']})")
        
    print("\nConfusion Matrix:")
    missions = list(test_suite.keys()) + ["UNKNOWN"]
    # Header
    header_label = "True \\ Pred"
    print(f"{header_label:>20} | " + " | ".join([f"{m[:5]:>5}" for m in missions]))
    for true_m in test_suite.keys():
        row = f"{true_m:>20} | "
        for pred_m in missions:
            row += f"{confusion_matrix[true_m][pred_m]:>5} | "
        print(row)
        
    print("\nTop Failures:")
    for f in failures:
        print(f"  [True: {f['true_mission']}, Pred: {f['predicted_mission']}, Conf: {f['confidence']:.2f}] Prompt: '{f['prompt']}'")
        
    # Write report
    report_path = r"C:\Users\srava\.gemini\antigravity\brain\de5955b7-0949-4384-9d8f-9ea18b737cd8\mission_detection_accuracy_report.md"
    
    with open(report_path, "w") as f:
        f.write("# Mission Detection Accuracy Report\n\n")
        f.write(f"**Overall Accuracy:** {overall_accuracy:.2f}%\n")
        f.write(f"**Total Prompts Tested:** {total_prompts}\n\n")
        
        f.write("## Per Mission Accuracy\n")
        for mission, stats in mission_accuracy.items():
            acc = (stats["correct"] / stats["total"]) * 100
            f.write(f"- **{mission}:** {acc:.2f}% ({stats['correct']}/{stats['total']})\n")
            
        f.write("\n## Confusion Matrix\n")
        f.write("| True \\ Pred | " + " | ".join([m for m in missions]) + " |\n")
        f.write("|---|" + "|".join(["---" for _ in missions]) + "|\n")
        for true_m in test_suite.keys():
            row = f"| **{true_m}** | "
            for pred_m in missions:
                row += f"{confusion_matrix[true_m][pred_m]} | "
            f.write(row + "\n")
            
        f.write("\n## Failure Cases\n")
        if failures:
            for fail in failures:
                f.write(f"- Prompt: *\"{fail['prompt']}\"*\n")
                f.write(f"  - **True Mission:** {fail['true_mission']}\n")
                f.write(f"  - **Predicted Mission:** {fail['predicted_mission']}\n")
                f.write(f"  - **Confidence:** {fail['confidence']:.2f}\n")
        else:
            f.write("No failures detected!\n")
            
if __name__ == "__main__":
    run_benchmark()
