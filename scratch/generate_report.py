import sys
sys.path.append('src')
from graph.service import GraphService
from data_ingestion.pipeline import generate_data_quality_report
import json

gs = GraphService()
missions = ['chicken_biryani', 'movie_night', 'house_party']
report = {
    'graph_integrity': generate_data_quality_report(),
    'mission_dependencies': {}
}

for m in missions:
    report['mission_dependencies'][m] = gs.get_mission_requirements_weighted(m)

with open('scratch/before_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Report generated at scratch/before_report.json")
