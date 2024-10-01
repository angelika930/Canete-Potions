from fastapi import APIRouter
import sqlalchemy
from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        row = result.fetchone()
        green_potions = row.num_green_potions

    if green_potions > 1:
        return [
        
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": green_potions,
                    "price": 30,
                    "potion_type": [0, 100, 0, 0],
                },
                
            
            ]
    else:
        return []

#For later versions
"""
  {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": row.num_red_potions,
                "price": 30,
                "potion_type": [100, 0, 0, 0],
            },

            {
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": row.num_blue_potions,
                "price": 30,
                "potion_type": [0, 0, 100, 0],
            }



"""