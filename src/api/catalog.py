from fastapi import APIRouter
import sqlalchemy
from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    with db.engine.begin() as connection:
        sku_query = connection.execute(sqlalchemy.text("SELECT sku FROM potion_options"))
        name_query = connection.execute(sqlalchemy.text("SELECT name FROM potion_options"))
        quantity_query = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_options"))
        potion_types_query = connection.execute(sqlalchemy.text("SELECT potion_type FROM potion_options"))
        price_query = connection.execute(sqlalchemy.text("SELECT price FROM potion_options"))

    #Formulate lists from query data
    sku_list = [sku[0] for sku in sku_query]
    name_list = [name[0] for name in name_query]
    quantity_list = [quantity[0] for quantity in quantity_query]
    potion_types_list = [potion[0] for potion in potion_types_query]
    price_list = [price[0] for price in price_query]
        

    catalog_plan = []
    
    #Add potions to catalog if they have enough inventory
    for i in range(len(potion_types_list)):
        if quantity_list[i] > 0:
            catalog_plan.append(
                    {
                    "sku": sku_list[i],
                    "name": name_list[i],
                    "quantity": quantity_list[i],
                    "price": price_list[i],
                    "potion_type": potion_types_list[i],
                     },)
      
    return catalog_plan

