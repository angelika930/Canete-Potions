from fastapi import APIRouter
import sqlalchemy
from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    
    with db.engine.begin() as connection:
        query = connection.execute(sqlalchemy.text("SELECT sku, name, quantities, potion_type, price FROM potion_options")).fetchall()

    catalog_plan = []
    
    #Add potions to catalog if they have enough inventory
    for i in range(len(query)):
        if query[i][2] > 0:
            catalog_plan.append(
                    {
                    "sku": query[i][0],
                    "name": query[i][1],
                    "quantity": query[i][2],
                    "potion_type": query[i][3],
                    "price": query[i][4]
                     },)
      
    return catalog_plan

