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
            result = connection.execute(sqlalchemy.text("SELECT num_green_ml, num_green_potions, gold FROM global_inventory"))
            row = result.fetchone()
            if row.gold >= barrel.price:
                update_gold = sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price")
                connection.execute(update_gold, {"price": barrel.price})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :ml"), {"ml": barrel.ml_per_barrel})
            
            else: break
     
           

            print("Current Gold: ", row.gold)
            print("potion type:", barrel.potion_type)

            #For later versions

            #ask if the price reflects each individual barrel or total cost
            """
            #Checks if potion type is red
            total_price = (barrel.quantity)*(barrel.price)
            total_ml = (barrel.quantity)*(barrel.ml_per_barrel)
            if barrel.potion_type[0] == 1 and row.gold >= total_price:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :ml"), {"ml": total_ml})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"), {"price": total_price})

            #Check if potion type is green
            elif barrel.potion_type[1] == 1 and row.gold >= total_price:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :ml"), {"ml": total_ml})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"), {"price": total_price})

            #Checks if potion type is blue
            elif barrel.potion_type[2] == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + :ml"), {"ml": total_ml})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"), {"price": total_price})

            
            """
            

    return []

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    barrel_bought = False

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml, gold FROM global_inventory"))

        row = result.fetchone()
            
    for barrel in wholesale_catalog:
        if barrel.sku == 'SMALL_GREEN_BARREL':

            if row.num_green_potions < 10 and row.gold >= barrel.price: 
                barrel_bought = True
                return [
                    {
                        "sku": "SMALL_GREEN_BARREL",
                        "quantity": 1
                    }
                
                ]

            print(barrel)
            break
    
    if barrel_bought == False:
        return []
    
    #For later versions
    """
    result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

    row = result.fetchone()

    #Checks that potions are available
    if row.num_green_ml == 0:
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]
    
    elif row.num_red_ml == 0:
        return [
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            }
        ]
    
    elif row.num_blue_ml == 0:
        return [
            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            }
        ]
    
    #Checks if there's a potion that's less than others

    elif row.red_potions_bought > row.green_potions_bought and row.red_potions_bought > row.blue_potions_bought:
        return [
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            }
        ]
    
    elif row.green_potions_bought > row.red_potions_bought and row.green_potions_bought > row.blue_potions_bought:
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]
    
    elif row.blue_potions_bought > row.green_potions_bought and row.blue_potions_bought > row.red_potions_bought:
        return [
            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            }
        ]

    elif row.red_potions_bought == row.green_potions_bought:
        return [
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            }
        ]
    
    elif row.green_potions_bought == row.blue_potions_bought:
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]

    elif row.red_potions_bought == row.blue_potions_bought:
        return [
            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            }
        ]
    
    else: return []

    
    
    
    """
    
    

