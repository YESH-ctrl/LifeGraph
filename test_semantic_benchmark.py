import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from engines.domains.mission_detection.service import MissionDetectionService
from engines.domains.mission_detection.schemas import MissionDetectionRequest

def run_benchmarks():
    service = MissionDetectionService()
    
    # Warmup the model so we don't count initialization time in latency
    print("Warming up model...")
    warmup_req = MissionDetectionRequest(text="hello world")
    service.detect(warmup_req)
    print("Model warmed up.\n")

    test_cases = [
        "My wife and I complete 10 years next month",
        "Our wedding milestone is coming",
        "Need something for our marriage celebration",
        "My friend turns 20 tomorrow",
        "We finally bought our first apartment",
        "Our baby arrives in a few weeks"
    ]
    
    total_time = 0.0
    
    print(f"{'Input Text':<50} | {'Detected Mission':<15} | {'Latency (ms)':<10}")
    print("-" * 85)
    
    for text in test_cases:
        req = MissionDetectionRequest(text=text)
        
        start = time.perf_counter()
        res = service.detect(req)
        end = time.perf_counter()
        
        latency_ms = (end - start) * 1000
        total_time += latency_ms
        
        print(f"{text:<50} | {res.detected_mission:<15} | {latency_ms:.2f} ms")
        
    print("-" * 85)
    print(f"Average Latency: {total_time / len(test_cases):.2f} ms per request")

if __name__ == "__main__":
    import sys
    import os
    # Add src to path so we can import properly
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    run_benchmarks()
