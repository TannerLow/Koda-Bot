from src.Database.database import Database
from src.API.model import Stats

def create_test_data_in_db(database: Database) -> None:
    database.set_record('users', 229270566798884874, {})

    stats: Stats = Stats(
        xp=0,
        xp_to_level=100,
        level=1
    )
    database.set_record('stats', 229270566798884874, stats)