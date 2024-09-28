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
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, gold, num_green_ml FROM global_inventory"))
        row = result.fetchone()

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    for barrel in barrels_delivered:
        print("hello")
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET :num_green_ml = :num_green_ml + :ml"), {"num_green_ml": row.num_green_ml, "ml": barrel.ml_per_barrel})
            update_gold = sqlalchemy.text("UPDATE global_inventory SET :gold = :gold - :price")
        with db.engine.begin() as connection:
            connection.execute(update_gold, {"gold": row.gold,"price": barrel.price})


    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions, gold FROM global_inventory"))

        row = result.fetchone()
            

    if row[0] < 10: 
        return [
            {
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            }
        ]

