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



    for potion in potions_delivered:
        with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            row = result.fetchone()
            if row.num_green_ml >= 100 and potion.potion_type == [0,100,0,0]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :green_potions"), {"green_potions": potion.quantity})
                total_ml = 100*(potion.quantity)
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - :potion_ml"), {"potion_ml": total_ml})

            elif row.num_red_ml >= 100 and potion.potion_type == [100,0,0,0]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + :red_potions"), {"red_potions": potion.quantity})
                total_ml = 100*(potion.quantity)
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_ml"), {"potion_ml": total_ml})
            
            elif row.num_blue_ml >= 100 and potion.potion_type == [0,0,100,0]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions + :blue_potions"), {"blue_potions": potion.quantity})
                total_ml = 100*(potion.quantity)
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - :potion_ml"), {"potion_ml": total_ml})


 
    return []

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into green potions.

    #red_potion_quantity = row.num_red_ml//100
    #blue_potion_quantity = row.num_blue_ml//100

    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            row = result.fetchone()

    bottle_plan = []
    potion_dict = {
                   'red': row.num_red_ml//100, 
                   'green': row.num_green_ml//100, 
                   'blue': row.num_blue_ml//100
                  }
    
    #Create dictionary of potion mapping
    potion_mapping = {
        'red': [100, 0, 0, 0],
        'green': [0, 100, 0, 0], 
        'blue': [0, 0, 100, 0],
        
         }

    for potion, quantity in potion_dict.items():

        if quantity >= 1:
            bottle_plan.append(
                {
                    "potion_type": potion_mapping[potion],
                    "quantity": quantity
                },
            )
    print(bottle_plan)
    return bottle_plan

    


    
   
    

if __name__ == "__main__":
    print(get_bottle_plan())