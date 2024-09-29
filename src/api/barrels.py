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
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        row = result.fetchone()

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    for barrel in barrels_delivered:
        print("hello")
        with db.engine.begin() as connection:

            #############    CHECK THIS FOR POTION TYPE OF BARREL??????      #######################

            #Checks if potion type is red
            if barrel.potion_type[0] == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :ml"), {"ml": barrel.ml_per_barrel})

            #Checks if potion type is green
            elif barrel.potion_type[1] == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :ml"), {"ml": barrel.ml_per_barrel})

            #Checks if potion type is blue
            elif barrel.potion_type[2] == 1:
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + :ml"), {"ml": barrel.ml_per_barrel})
            
            #Update gold accordingly
            update_gold = sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price")
            connection.execute(update_gold, {"price": barrel.price})
            print("Current Gold: ", row.gold)
            print("potion type:", barrel.potion_type)
            print("LENGTH OF POTION TYPE: ", len(barrel.potion_type))


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

        row = result.fetchone()
            

    if row.num_green_potions < 10 and row.num_red_potions < 10 and row.num_blue_potions < 10: 
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
          
        ]
    
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

