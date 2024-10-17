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
            potion_types = connection.execute(sqlalchemy.text("SELECT potion_type FROM potion_options"))
            list_types =  [potion_type[0] for potion_type in potion_types]



            if potion.potion_type == list_types[0]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_red_amount, num_green_ml = num_green_ml - :potion_green_amount, num_blue_ml = num_blue_ml - :potion_blue_amount, num_dark_ml = num_dark_ml - :potion_dark_amount "), 
                                   {"potion_red_amount": list_types[0][0], "potion_green_amount": list_types[0][1], "potion_blue_amount": list_types[0][2], "potion_dark_amount": list_types[0][3]})
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity + :potion_quantity WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1);"), {"potion_quantity": potion.quantity})

            elif potion.potion_type == list_types[1]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_red_amount, num_green_ml = num_green_ml - :potion_green_amount, num_blue_ml = num_blue_ml - :potion_blue_amount, num_dark_ml = num_dark_ml - :potion_dark_amount "), 
                                   {"potion_red_amount": list_types[1][0], "potion_green_amount": list_types[1][1], "potion_blue_amount": list_types[1][2], "potion_dark_amount": list_types[1][3]})
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity + :potion_quantity WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 1);"), {"potion_quantity": potion.quantity})
            
            elif potion.potion_type == list_types[2]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_red_amount, num_green_ml = num_green_ml - :potion_green_amount, num_blue_ml = num_blue_ml - :potion_blue_amount, num_dark_ml = num_dark_ml - :potion_dark_amount "), 
                                   {"potion_red_amount": list_types[2][0], "potion_green_amount": list_types[2][1], "potion_blue_amount": list_types[2][2], "potion_dark_amount": list_types[2][3]})
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity + :potion_quantity WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 2);"), {"potion_quantity": potion.quantity})
            
            elif potion.potion_type == list_types[3]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_red_amount, num_green_ml = num_green_ml - :potion_green_amount, num_blue_ml = num_blue_ml - :potion_blue_amount, num_dark_ml = num_dark_ml - :potion_dark_amount "), 
                                    {"potion_red_amount": list_types[3][0], "potion_green_amount": list_types[3][1], "potion_blue_amount": list_types[3][2], "potion_dark_amount": list_types[3][3]})
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity + :potion_quantity WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 3);"), {"potion_quantity": potion.quantity})

            elif potion.potion_type == list_types[4]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_red_amount, num_green_ml = num_green_ml - :potion_green_amount, num_blue_ml = num_blue_ml - :potion_blue_amount, num_dark_ml = num_dark_ml - :potion_dark_amount "), 
                                    {"potion_red_amount": list_types[4][0], "potion_green_amount": list_types[4][1], "potion_blue_amount": list_types[4][2], "potion_dark_amount": list_types[4][3]})
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity + :potion_quantity WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 4);"), {"potion_quantity": potion.quantity})

            elif potion.potion_type == list_types[5]:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :potion_red_amount, num_green_ml = num_green_ml - :potion_green_amount, num_blue_ml = num_blue_ml - :potion_blue_amount, num_dark_ml = num_dark_ml - :potion_dark_amount "), 
                                   {"potion_red_amount": list_types[5][0], "potion_green_amount": list_types[5][1], "potion_blue_amount": list_types[5][2], "potion_dark_amount": list_types[5][3]})
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity + :potion_quantity WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 5);"), {"potion_quantity": potion.quantity})

            
 
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
            potion_types = connection.execute(sqlalchemy.text("SELECT potion_type FROM potion_options"))
            row_count =  connection.execute(sqlalchemy.text("SELECT COUNT(*) FROM potion_options"))
        

    # Extract values from the result
    red_quantity = [potion_type[0] for potion_type in red_ml_query]
    blue_quantity = [potion_type[0] for potion_type in blue_ml_query]
    green_quantity = [potion_type[0] for potion_type in green_ml_query]
    list_types =  [potion_type[0] for potion_type in potion_types]
   
    row_count = row_count.scalar()
 


    #Find remaining ml
    remaining_red = row.num_red_ml
    remaining_blue = row.num_blue_ml
    remaining_green = row.num_green_ml

    quantity_dict = {0 : 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

   #Find how much of each bottle can be bottled

    count = 0
    while (remaining_red - red_quantity[count] >= 0 and remaining_blue - blue_quantity[count] >= 0 and remaining_green - green_quantity[count] >= 0):    
        quantity_dict[count] += 1

        count += 1
      

        if (count == row.count):
            count = 0
       
            
         
    for i in range(row_count):

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