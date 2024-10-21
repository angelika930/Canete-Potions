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
    
    
    #Create dictionary of potion mapping
    potion_mapping = {
        'red': [100, 0, 0, 0],
        'green': [0, 100, 0, 0], 
        'blue': [0, 0, 100, 0],
        
         }
    
    #pull how much red, green, and blue ml needed for all potions and grab number of potions being grabbed
    with db.engine.begin() as connection:
            red_ml_query = connection.execute(sqlalchemy.text("SELECT red FROM potion_options"))
            green_ml_query = connection.execute(sqlalchemy.text("SELECT green FROM potion_options"))
            blue_ml_query = connection.execute(sqlalchemy.text("SELECT blue FROM potion_options"))
            dark_ml_query = connection.execute(sqlalchemy.text("SELECT dark FROM potion_options"))
            potion_types = connection.execute(sqlalchemy.text("SELECT potion_type FROM potion_options"))
            row_count =  connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM potion_options"))
        

    # Extract values from the result
    red_quantity = [potion_type[0] for potion_type in red_ml_query]
    blue_quantity = [potion_type[0] for potion_type in blue_ml_query]
    green_quantity = [potion_type[0] for potion_type in green_ml_query]
    dark_quantity = [potion_type[0] for potion_type in dark_ml_query]
    list_types =  [potion_type[0] for potion_type in potion_types]
   
    row_count = row_count.scalar()
    print("Row count: ", row_count)
 


    #Find remaining ml
    remaining_red = row.num_red_ml
    remaining_blue = row.num_blue_ml
    remaining_green = row.num_green_ml

    print("REMAINING RED: ", remaining_red)
    print("REMAINING BLUE: ", remaining_blue)
    print("REMAINING GREEN: ", remaining_green)
    
    quantity_dict = {0 : 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

   #Find how much of each bottle can be bottled
    print("BLUE QUANTITY: ", blue_quantity)
    print("RED QUANTITY: ", red_quantity)
    print("GREEN QUANTITY: ", green_quantity)
    print("DARK QUANTITY: ", dark_quantity)

    count = 0
    while (remaining_red - red_quantity[count] >= 0 and remaining_blue - blue_quantity[count] >= 0 and remaining_green - green_quantity[count] >= 0):    
        quantity_dict[count] += 1

        count += 1
        print("COUNT: ", count)

        print("RED_QUANTITY [COUNT]: ", red_quantity[count])
        print("GREEN_QUANTITY [COUNT]: ", green_quantity[count])
        print("BLUE_QUANTITY [COUNT]: ", blue_quantity[count])
        print("QUANTITY _DICT: ", quantity_dict[count])

        if (count == row.count):
            count = 0
       
            
         
    for i in range(row_count):
        if quantity_dict[i] != 0:
            bottle_plan.append(
                {
                    "potion_type": list_types[i],
                    "quantity": quantity_dict[i]
                },
            )
    print("Bottle plan: ", bottle_plan)
    return bottle_plan

    


    
   
    

if __name__ == "__main__":
    print(get_bottle_plan())