from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


global has_ml
has_ml = True

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
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        row = result.fetchone()
        potion_types = connection.execute(sqlalchemy.text("SELECT potion_type FROM potion_options"))
        list_types =  [potion_type[0] for potion_type in potion_types]
    
        potions_to_add = {1: 0,
                          2: 0,
                          3: 0,
                          4: 0,
                          5: 0,
                          6: 0}
        
        potion_variety = [list_types[0], list_types[1], list_types[2], list_types[3], list_types[4], list_types[5]]
        

        
        for potion in potions_delivered:
            red_ml_change += potion.potion_type[0] * potion.quantity
            green_ml_change += potion.potion_type[1] * potion.quantity
            blue_ml_change += potion.potion_type[2] * potion.quantity
            dark_ml_change += potion.potion_type[3] * potion.quantity

            if potion.potion_type == list_types[0]:
                potions_to_add[1] += potion.quantity
            
            elif potion.potion_type == list_types[1]:
                potions_to_add[2] += potion.quantity
            
            elif potion.potion_type == list_types[2]:
                potions_to_add[3] += potion.quantity
            
            elif potion.potion_type == list_types[3]:
                potions_to_add[4] += potion.quantity
            
            elif potion.potion_type == list_types[4]:
                potions_to_add[5] += potion.quantity

            elif potion.potion_type == list_types[5]:
                potions_to_add[6] += potion.quantity

        print("before connection")
        with db.engine.begin() as connection:    
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_red_amount, num_green_ml = num_green_ml - :potion_green_amount, num_blue_ml = num_blue_ml - :potion_blue_amount,  num_dark_ml = num_dark_ml - :potion_dark_amount"), {"potion_red_amount":red_ml_change, "potion_green_amount": green_ml_change, "potion_blue_amount": blue_ml_change, "potion_dark_amount": dark_ml_change})

            #update potion quantities         
            connection.execute(sqlalchemy.text(" UPDATE potion_options SET quantity = quantity + :quantity WHERE id = 1"), {"quantity": potions_to_add[1]})
            connection.execute(sqlalchemy.text(" UPDATE potion_options SET quantity = quantity + :quantity WHERE id = 2"), {"quantity": potions_to_add[2]})
            connection.execute(sqlalchemy.text(" UPDATE potion_options SET quantity = quantity + :quantity WHERE id = 3"), {"quantity": potions_to_add[3]})
            connection.execute(sqlalchemy.text(" UPDATE potion_options SET quantity = quantity + :quantity WHERE id = 4"), {"quantity": potions_to_add[4]})
            connection.execute(sqlalchemy.text(" UPDATE potion_options SET quantity = quantity + :quantity WHERE id = 5"), {"quantity": potions_to_add[5]})
            connection.execute(sqlalchemy.text(" UPDATE potion_options SET quantity = quantity + :quantity WHERE id = 6"), {"quantity": potions_to_add[6]})
                                                    
 
    return []

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    global has_ml

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into green potions.

    #red_potion_quantity = row.num_red_ml//100
    #blue_potion_quantity = row.num_blue_ml//100

    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            row = result.fetchone()
            potion_types = connection.execute(sqlalchemy.text("SELECT potion_type FROM potion_options")).fetchall()

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
    while remaining_red >= 10 or remaining_blue >= 10 or remaining_green >= 10:
        for i in range(6):
            
            if (remaining_red - potion_options[i][0] >= 0 and remaining_green - potion_options[i][1] >= 0 and remaining_blue - potion_options[i][2] >= 0  and remaining_dark - potion_options[i][3] >= 0):

                if tuple(potion_options[i]) not in quantity_dict:
                    quantity_dict[tuple(potion_options[i])] = 1
                
                elif tuple(potion_options[i]) in quantity_dict:
                    quantity_dict[tuple(potion_options[i])] += 1

            remaining_red -= potion_options[i][0]
            remaining_green -= potion_options[i][1]
            remaining_blue -= potion_options[i][2]
            remaining_dark -= potion_options[i][3]


    
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