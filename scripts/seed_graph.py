import os
import sys

# Add src directory to path so we can import domains
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from domains.missions.models import MissionModel
from domains.missions.repository import MissionRepository
from domains.relationships.models import RelationshipModel
from domains.relationships.repository import RelationshipRepository
from domains.relationships.schemas import RelationshipType

def seed():
    mission_repo = MissionRepository()
    rel_repo = RelationshipRepository()

    print("Seeding Missions...")
    missions = [
        MissionModel("BIRTHDAY", "Birthday Party", "Organize a birthday celebration", "EVENT"),
        MissionModel("FITNESS", "Fitness Journey", "Start a healthy fitness routine", "LIFESTYLE"),
        MissionModel("MOVIE_NIGHT", "Movie Night", "Host a movie night at home", "ENTERTAINMENT"),
        MissionModel("ROAD_TRIP", "Road Trip", "Plan an epic road trip", "TRAVEL"),
        MissionModel("HOUSE_WARMING", "House Warming", "Host a house warming party", "EVENT")
    ]
    
    for m in missions:
        mission_repo.create_mission(m)
        print(f" Created Mission: {m.mission_id}")

    print("\nSeeding Relationships...")
    relationships = [
        # Birthday
        ("BIRTHDAY", "CAKE001"),
        ("BIRTHDAY", "CANDLE001"),
        ("BIRTHDAY", "DRINK001"),
        ("BIRTHDAY", "SNACK001"),
        
        # Fitness
        ("FITNESS", "PROTEIN001"),
        ("FITNESS", "OATS001"),
        ("FITNESS", "WATER_BOTTLE001"),
        ("FITNESS", "GYM_GLOVES001"),
        
        # Movie Night
        ("MOVIE_NIGHT", "POPCORN001"),
        ("MOVIE_NIGHT", "SOFT_DRINK001"),
        ("MOVIE_NIGHT", "CHIPS001")
    ]

    for mission_id, product_id in relationships:
        rel = RelationshipModel(
            source_type="MISSION",
            source_id=mission_id,
            target_type="PRODUCT",
            target_id=product_id,
            relationship_type=RelationshipType.REQUIRES.value
        )
        rel_repo.create_relationship(rel)
        print(f" Created Relationship: {mission_id} REQUIRES {product_id}")

    print("\nSeed complete!")

if __name__ == "__main__":
    seed()
