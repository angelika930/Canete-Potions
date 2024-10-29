from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random

sell_green = True

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
    
    red_ml_change = 0
    blue_ml_change = 0
    green_ml_change = 0
    dark_ml_change = 0
    gold_change = 0
       

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    for barrel in barrels_delivered:

        gold_change += (barrel.quantity)*(barrel.price)

        if barrel.potion_type == [1,0,0,0]:
            red_ml_change += (barrel.quantity)*(barrel.ml_per_barrel)

        elif barrel.potion_type == [0,1,0,0]:
            green_ml_change += (barrel.quantity)*(barrel.ml_per_barrel)

        elif barrel.potion_type == [0,0,1,0]:
            blue_ml_change += (barrel.quantity)*(barrel.ml_per_barrel)
        
        elif barrel.potion_type == [0,0,0,1]:
            dark_ml_change += (barrel.quantity)*(barrel.ml_per_barrel)

        print("GREEN ML: ", green_ml_change)
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"), {"price": gold_change})
        print("GOLD CHANGE: ", gold_change)
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :red_ml_change, num_green_ml = num_green_ml + :green_ml_change, num_blue_ml = num_blue_ml + :blue_ml_change, num_dark_ml = num_dark_ml + :dark_ml_change"), {"red_ml_change": red_ml_change, "green_ml_change": green_ml_change, "blue_ml_change": blue_ml_change, "dark_ml_change": dark_ml_change})

    return []

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):

    global sell_green

    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        row = result.fetchone()
    
    result = []

    barrel_quantity = {'red': 0, 'blue': 0, 'green': 0}
    barrel_prices = {'red': 100, 'green': 100, 'blue': 120}
    budget = 0
    colors_bought = []
    barrel_types = ["red", "blue", "green"]
    

    #If we are poor 
    if row.gold >= 100 and row.gold < 120:
        if random.choice(barrel_types) == "green" :
            sell_green = False
            return  [
                    {
                        "sku": "MINI_GREEN_BARREL", 
                        "quantity": 1 
                    }
            ]

        elif random.choice(barrel_types ) == 'red':
            sell_green = True
            return  [
                    {
                        "sku": "MINI_RED_BARREL", 
                        "quantity": 1
                    }
            ]
        
        elif random.choice(barrel_types ) == 'blue':
            return [
                {
                    "sku": "MINI_BLUE_BARREL", 
                    "quantity": 1 
                }                
            ]
        
    elif row.gold >= 120 and row.gold < 320:
         return  [
                    {
                        "sku": "MINI_BLUE_BARREL", 
                        "quantity": 1 
                    },
                     {
                        "sku": "MINI_RED_BARREL", 
                        "quantity": 1
                    }

            ]

    #If we are getting ourselves off the ground
    elif row.gold > 320:

        
        return [
            {
                "sku": "SMALL_RED_BARREL", 
                "quantity": 1
            },
             {
                "sku": "SMALL_BLUE_BARREL", 
                "quantity": 1
            },
              {
                "sku": "SMALL_GREEN_BARREL", 
                "quantity": 1 
            }
        ]
    
    elif row.gold > 600:

        #Determine what color barrels to buy
        if row.num_green_ml < 1000:
            colors_bought.append('green')
        if row.num_blue_ml < 1000:
            colors_bought.append('blue')
        if row.num_red_ml < 1000:
            colors_bought.append('red')


        #Determine what barrel budget is
        if len(colors_bought) == 0:
            return []
        elif len(colors_bought) == 1:
            budget = 200
        elif len(colors_bought) == 2:
            budget = 400
        else: budget = 600

        #buy as many barrels as possible, iterating through colors in colors_bought array
        index = 0
        price_of_barrel = barrel_prices[colors_bought[index]]
        while  budget - price_of_barrel  >= 0:
            if colors_bought[index] == 'red':
                barrel_quantity['red'] += 1
            
            elif colors_bought[index] == 'blue':
                barrel_quantity['blue'] += 1

            elif colors_bought[index] == 'green':
                barrel_quantity['green'] += 1

            index += 1
            if index >= len(colors_bought):
                index = 0

            price_of_barrel = barrel_prices[colors_bought[index]]


        #Return json response
        for i in range(len(colors_bought)):
            if colors_bought[i] == 'red':
                result.append( {
                        "sku": "SMALL_RED_BARREL", 
                        "quantity": barrel_quantity['red'] 
                    },)
            
            elif colors_bought[i] == 'blue':
                result.append( {
                        "sku": "SMALL_BLUE_BARREL", 
                        "quantity": barrel_quantity['blue'] 
                    },)
                
            elif colors_bought[i] == 'green':
                result.append( {
                        "sku": "SMALL_GREEN_BARREL", 
                        "quantity": barrel_quantity['green'] 
                    },)
        print("BARRELS WANTED: ", result)
        return result



    
    
    
    
    
    

