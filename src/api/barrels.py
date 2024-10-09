from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db




router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    
       
       

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    for barrel in barrels_delivered:
        with db.engine.begin() as connection:
            #Update gold accordingly
            result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
            row = result.fetchone()
            total_price = (barrel.quantity)*(barrel.price)

            if row.gold >= total_price:
                print("total price: ", (barrel.quantity)*(barrel.price))
                with db.engine.begin() as connection:
                  connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"), {"price": total_price})
                total_ml = (barrel.quantity)*(barrel.ml_per_barrel)

                if barrel.potion_type == [0,1,0,0]:
                    with db.engine.begin() as connection:
                        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :ml"), {"ml": total_ml})

                elif barrel.potion_type == [1,0,0,0]:
                    with db.engine.begin() as connection:
                        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :ml"), {"ml": total_ml})
                
                elif barrel.potion_type == [0,0,1,0]:
                    with db.engine.begin() as connection:
                        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + :ml"), {"ml": total_ml})
        
        print("Barrel sku: ", barrel.sku)     
    with db.engine.begin() as connection:     
         result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
         row = result.fetchone() 
         print("Current Gold: ", row.gold)

    #For later versions

    #ask if the price reflects each individual barrel or total cost

    return []

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        row = result.fetchone()
    
    desired_barrel = ""

    if row.num_blue_potions == 0:
        desired_barrel = "blue"
    
    elif row.num_red_potions == 0:
        desired_barrel = "red"
        

    elif row.num_green_potions == 0:
        desired_barrel = "green"
       
    #Checks if there's a potion that's bought more than others

    elif row.red_potions_bought > row.green_potions_bought and row.red_potions_bought > row.blue_potions_bought:
        desired_barrel = "red"
    
    elif row.green_potions_bought > row.red_potions_bought and row.green_potions_bought > row.blue_potions_bought:
        desired_barrel = "green"
    
    elif row.blue_potions_bought > row.green_potions_bought and row.blue_potions_bought > row.red_potions_bought:
        desired_barrel = "blue"

    elif row.red_potions_bought == row.green_potions_bought:
        desired_barrel = "red"
    
    elif row.green_potions_bought == row.blue_potions_bought:
       desired_barrel = "green"

    elif row.red_potions_bought == row.blue_potions_bought:
       desired_barrel = "blue"
    
    else: desired_barrel = "none"

    if desired_barrel == "none" or row.gold < 60:
        return []

    elif row.gold >= 100:
        print(desired_barrel)
        if desired_barrel == "red":
            return [
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            }
        ]

        elif desired_barrel == "blue":
            return [
            {
                "sku": "MINI_BLUE_BARREL",
                "quantity": 1,
            }
        ]

        else:
            return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]

    
    
    
    
    
    

