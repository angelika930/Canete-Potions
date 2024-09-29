from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    
    row = result.fetchone()

    for potion in potions_delivered:
        if potion.potion_type[0] == 'r':
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + :red_potions"), {"red_potions": potion.quantity})

        elif potion.potion_type[1] == 'g':
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :green_potions"), {"green_potions": potion.quantity})

        elif potion.potion_type[2] == 'b':
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions + :blue_potions"), {"blue_potions": potion.quantity})
 
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into green potions.

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
    
    row = result.fetchone()
    
    green_potion_quantity = row.num_green_ml//100
    red_potion_quantity = row.num_red_ml//100
    blue_potion_quantity = row.num_blue_ml//100


    return [
        {
            "potion_type": [0, 100, 0, 0],
            "quantity": green_potion_quantity,
        },

        {
            "potion_type": [100, 0, 0, 0],
            "quantity": red_potion_quantity,
        },

        {
            "potion_type": [0, 0, 100, 0],
            "quantity": blue_potion_quantity,
        }
    ]
    
   
    

if __name__ == "__main__":
    print(get_bottle_plan())