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

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))

        row = result.fetchone()

        if row[0] < 10:
            for barrel in barrels_delivered:
                if barrel.sku.__contains__("green") and row[2] >= barrel.price:        #CHECK THIS 
                    connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + 1"))
                    update_gold = sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price")
                    connection.execute(update_gold, {"price": barrel.price})
                break
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]

