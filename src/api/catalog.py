from fastapi import APIRouter
import sqlalchemy
from src import database as db



router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    

    with db.engine.begin() as connection:
        query = connection.execute(sqlalchemy.text("SELECT SUM(potion_inventory.quantity) as total_quantity,"
                                                   "potion_options.sku, potion_options.name, potion_options.potion_type, "
                                                   "potion_options.price FROM potion_inventory " 
                                                    "JOIN potion_options ON potion_options.potion_type = potion_inventory.potion_type "
                                                    "GROUP BY potion_options.potion_type, " 
                                                    "potion_options.sku, potion_options.name, "  
                                                    "potion_options.price")).fetchall()

    catalog_plan = []
    
    #Add potions to catalog if they have enough inventory
    for i in range(len(query)):
        if query[i][0] > 0:
            catalog_plan.append(
                    {
                    "sku": query[i][1],
                    "name": query[i][2],
                    "quantity": query[i][0],
                    "potion_type": query[i][3],
                    "price": query[i][4]
                     },)
      
    return catalog_plan

