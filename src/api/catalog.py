from fastapi import APIRouter
import sqlalchemy
from src import database as db




router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    with db.engine.begin() as connection:
        print("HEREEEEEEEEE1")
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        print("HEREEEEEEEEE2")
        row = result.fetchone()
        print("HEREEEEEEEEE3")
    
    """
    Each unique item combination must have only a single price.
    """

    """
        return [
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": 1,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]

    
    """

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
                "quantity": row[0],
                "price": 30,
                "potion_type": [0, 100, 0, 0],
            },
        ]
