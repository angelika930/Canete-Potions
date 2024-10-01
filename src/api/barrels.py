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
            """
            #Checks if potion type is red
            if barrel.potion_type[0] == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :ml"), {"ml": barrel.ml_per_barrel})

            #Checks if potion type is blue
            elif barrel.potion_type[2] == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + :ml"), {"ml": barrel.ml_per_barrel})
            
            """
            

            

           
            
            


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, num_green_ml, gold FROM global_inventory"))

        row = result.fetchone()
            
    for barrel in wholesale_catalog:
        if barrel.sku == 'SMALL_GREEN_BARREL':

            if row.num_green_potions < 10 and row.gold >= barrel.price: 
                return [
                    {
                        "sku": "SMALL_GREEN_BARREL",
                        "quantity": 1,

                        "sku": "SMALL_GREEN_BARREL",
                        "ml_per_barrel": 500,
                        "potion_type": [0, 1, 0, 0], 
                        "price": 100,
                        "quantity": 10
                    }
                
                ]

            print(barrel)
            break
    
    #For later versions
    """
    elif row.num_red_potions < 10 and row.num_green_potions < 10 and not(row.num_blue_potions < 10):
        return [
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            },
            
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]
    
    elif row.num_green_potions < 10 and row.num_blue_potions < 10 and not(row.num_red_potions < 10):
        return [
            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            },

            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]
    
    elif row.num_red_potions < 10 and row.num_blue_potions < 10 and not(row.num_green_potions < 10):
         return [
            {
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            },

            {
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            }
        ]

    else: return "NO BARRELS NEEDED"
    
    
    """
    
    

