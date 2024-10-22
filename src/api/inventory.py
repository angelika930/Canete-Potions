from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """

    num_potions = 0
    num_ml = 0

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT name, quantity FROM potion_options"))
        ml_result = connection.execute(sqlalchemy.text("SELECT num_green_ml, num_red_ml, num_blue_ml, num_dark_ml, gold FROM global_inventory"))
        ml_result = ml_result.fetchall()
        row = result.fetchall()
        
        num_ml = ml_result[0][0] + ml_result[0][1] + ml_result[0][2] + ml_result[0][3]
        for i in range(len(row)):
            num_potions += row[i][1]

        
        return {
              "number_of_potions": num_potions,
                "ml_in_barrels": num_ml,
                "gold": ml_result[0][4]
        }

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
