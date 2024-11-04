from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


global valid_bottle
valid_bottle = True

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

    red_ml_change = 0
    green_ml_change = 0
    blue_ml_change = 0
    dark_ml_change = 0
  
    
    potion_dict = {}
    
    for potion in potions_delivered:
        red_ml_change += potion.potion_type[0] * potion.quantity
        green_ml_change += potion.potion_type[1] * potion.quantity
        blue_ml_change += potion.potion_type[2] * potion.quantity
        dark_ml_change += potion.potion_type[3] * potion.quantity

        potion_dict[tuple(potion.potion_type)] = potion.quantity
    print("DICTIONARY: ", potion_dict)
    
    with db.engine.begin() as connection:    
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml)"
                                        "VALUES (:gold, :red, :green, :blue, :dark)"),
                                        {
                                            "gold": 0, "red": -red_ml_change, "blue": -blue_ml_change, 
                                            "green": -green_ml_change, "dark": -dark_ml_change
                                        
                                        })
    

        for key, value in potion_dict.items():
            #update potion quantities       
            connection.execute(sqlalchemy.text("INSERT INTO potion_inventory (potion_type, quantity)"
                                        "VALUES (:potion_type, :quantity)"),
                                        {
                                            "potion_type": list(key),
                                            "quantity": value
                                        
                                        })


    return []

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    global valid_bottle

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into green potions.

    #red_potion_quantity = row.num_red_ml//100
    #blue_potion_quantity = row.num_blue_ml//100

    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            row = result.fetchone()
            potion_types = connection.execute(sqlalchemy.text("SELECT potion_type, quantity FROM potion_options")).fetchall()

    bottle_plan = []
    potion_options = []

    quantity_dict = {}

    #Find remaining ml
    remaining_red = row.num_red_ml
    remaining_blue = row.num_blue_ml
    remaining_green = row.num_green_ml
    remaining_dark = row.num_dark_ml
    
    #populate list potion_options with potion recipes
    for i in range(len(potion_types)):
        potion_options.append(potion_types[i][0])

    #Print statements for testing
    print('REMAINING GREEN: ', remaining_green)
    print('REMAINING red: ', remaining_red)
    print('REMAINING blue: ', remaining_blue)
    print('REMAINING dark: ', remaining_dark)

    #Checks each potion to see how much ml can be used 
    while valid_bottle:

        valid_bottle = False

        for i in range(6):
            
            if (remaining_red - potion_options[i][0] >= 0 and remaining_green - potion_options[i][1] >= 0 and 
                remaining_blue - potion_options[i][2] >= 0  and remaining_dark - potion_options[i][3] >= 0):

                if tuple(potion_options[i]) not in quantity_dict:
                    quantity_dict[tuple(potion_options[i])] = 1
                
                elif tuple(potion_options[i]) in quantity_dict:
                    quantity_dict[tuple(potion_options[i])] += 1

                remaining_red -= potion_options[i][0]
                remaining_green -= potion_options[i][1]
                remaining_blue -= potion_options[i][2]
                remaining_dark -= potion_options[i][3]

                valid_bottle = True

        

    #Add recipes with quantity > 1 to bottle plan using dictionary
    for key, value in quantity_dict.items():
        if value > 0:
            bottle_plan.append(
                {
                    "potion_type": key,
                    "quantity": value
                },
            )
    print("Bottle plan: ", bottle_plan)
    return bottle_plan

    


    
   
    

if __name__ == "__main__":
    print(get_bottle_plan())