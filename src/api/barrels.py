from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random

sell_green = False
sell_blue = False
sell_red = False

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
        
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml)"
                                           "VALUES (:gold, :red, :green, :blue, :dark)"),
                                           {
                                               "gold": -gold_change, "red": red_ml_change, "blue": blue_ml_change, 
                                               "green": green_ml_change, "dark": dark_ml_change
                                            
                                            })
        print("GOLD CHANGE: ", gold_change)

    return []

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):

    print(wholesale_catalog)
    """
    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT SUM(gold), SUM(num_red_ml), SUM(num_green_ml), SUM(num_blue_ml), SUM(num_dark_ml)"
                                                  "FROM test_global_inventory_duplicate")).fetchall()
        
    gold = inventory[0][0]
    print("GOLD: ", gold)
    num_red_ml = inventory[0][1]
    num_green_ml = inventory[0][2]
    num_blue_ml = inventory[0][3]
    num_dark_ml = inventory[0][4]
    color_barrel = ""
    

    #Sort barrel list by price
    wholesale_catalog.sort(key=lambda barrel: barrel.price)
    print("catalog: ", wholesale_catalog)

    #initialize barrel plan
    barrel_plan = []

    capacity = 0
    if gold < 500:
        capacity = 500

    elif gold >= 500:
        capacity = 1000

    elif gold >= 1000:
        capacity = 1500


    for barrel in wholesale_catalog:
        sku = barrel.sku.lower()
        ml = barrel.ml_per_barrel
        potion_type = barrel.potion_type
        price = barrel.price
        quantity = barrel.quantity

        
        if sku.__contains__('red'):
            color_barrel = num_red_ml
            
        elif sku.__contains__('blue'):
            color_barrel = num_blue_ml
            
        elif sku.__contains__('green'):
            color_barrel = num_green_ml

        if sku.__contains__('dark'):
            color_barrel = num_dark_ml

        #Buy barrels based on the amount of money we have
        
        if gold - price >= 0 and capacity - color_barrel >= 0:
            if (gold < 120 and sku.__contains__("mini")) or (gold >= 120 and sku.__contains__("small")) or (gold >= 1000 and sku.__contains__("large")):
                barrel_plan.append({
                    "sku": sku,
                    "quantity": 1
                },)
                capacity = capacity - color_barrel
                gold = gold - price

    print("Barrel Plan: ", barrel_plan)
    return barrel_plan
    """

    

    with db.engine.begin() as connection:
        inventory = connection.execute(sqlalchemy.text("SELECT SUM(gold), SUM(num_red_ml), SUM(num_green_ml), SUM(num_blue_ml), SUM(num_dark_ml)"
                                                  "FROM global_inventory")).fetchall()
        
        gold = inventory[0][0] 
        num_red_ml = inventory[0][1]
        num_green_ml = inventory[0][2]
        num_blue_ml = inventory[0][3]
        num_dark_ml = inventory[0][4]

      
    result = []

    barrel_quantity = {'red': 0, 'blue': 0, 'green': 0}
    barrel_prices = {'red': 100, 'green': 100, 'blue': 120}
    budget = 0
    colors_bought = []
    barrel_types = ["red", "blue", "green"]
    

    #If we are poor 
    if gold >= 100 and gold < 120:
       
        if random.choice(barrel_types) == "green":
          
            print("BARREL BOUGHT: Mini Green Barrel")
            return  [
                    {
                        "sku": "MINI_GREEN_BARREL", 
                        "quantity": 1 
                    }
            ]

        elif random.choice(barrel_types ) == 'red':
            print("BARREL BOUGHT: Mini RED Barrel")
            return  [
                    {
                        "sku": "MINI_RED_BARREL", 
                        "quantity": 1
                    }
            ]
        
        elif random.choice(barrel_types ) == 'blue':
            print("BARREL BOUGHT: Mini BLUE Barrel")
            return [
                {
                    "sku": "MINI_BLUE_BARREL", 
                    "quantity": 1 
                }                
            ]
        
    elif gold >= 120 and gold < 180:
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
    
    elif gold > 180 and gold < 320:
         return  [
                {
                    "sku": "MINI_BLUE_BARREL", 
                    "quantity": 1 
                },
                    {
                    "sku": "MINI_RED_BARREL", 
                    "quantity": 1
                },
                    {
                    "sku": "MINI_GREEN_BARREL", 
                    "quantity": 1 
                }

            ]

    #If we are getting ourselves off the ground
    elif gold > 320:
        print("Bought small barrels of 3 colors")
        
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
    
    elif gold > 600:

        #Determine what color barrels to buy
        if num_green_ml < 1000:
            colors_bought.append('green')
        if num_blue_ml < 1000:
            colors_bought.append('blue')
        if num_red_ml < 1000:
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




    
    
    
    
    
    

