from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db


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
    

    #If we are poor 
    if row.gold >= 100 and row.gold < 120:
        if sell_green:
            sell_green = False
            return  [
                    {
                        "sku": "SMALL_GREEN_BARREL", 
                        "quantity": "1" 
                    }
            ]

        else:
            sell_green = True
            return  [
                    {
                        "sku": "SMALL_RED_BARREL", 
                        "quantity": "1" 
                    }
            ]
        

    #If we are getting ourselves off the ground
    elif row.gold > 320:

        
        return [
            {
                "sku": "SMALL_RED_BARREL", 
                "quantity": "1" 
            },
             {
                "sku": "SMALL_BLUE_BARREL", 
                "quantity": "1" 
            },
              {
                "sku": "SMALL_GREEN_BARREL", 
                "quantity": "1" 
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



    
    
    
    
    
    

