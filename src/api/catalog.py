from fastapi import APIRouter
import sqlalchemy
from src import database as db




router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        row = result.fetchone()
        
    

    return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": 1,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            },
            
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": row.num_green_potions,
                "price": 30,
                "potion_type": [0, 100, 0, 0],
            },
        ]
