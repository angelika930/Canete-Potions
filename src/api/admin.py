from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
            res = connection.execute(sqlalchemy.text("SELECT SUM(CAST(gold AS INTEGER)),  SUM(CAST(num_red_ml AS INTEGER))," 
                                    "SUM(CAST(num_green_ml AS INTEGER)), SUM(CAST(num_blue_ml AS INTEGER)), SUM(CAST(num_dark_ml AS INTEGER))" 
                                    "FROM global_inventory")).fetchall()
            gold = -(res[0][0] - 100)
            red = -res[0][1]
            green = -res[0][2]
            blue = -res[0][3]
            dark = -res[0][4]

            connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold, num_red_ml, num_green_ml, num_blue_ml, num_dark_ml)"
                                           "VALUES (:gold, :red, :green, :blue, :dark)"),
                                           {
                                               "gold": gold , "red": red,  
                                               "green": green, "blue": blue, "dark": dark
                                            
                                            }
                                           
                                           )
            
            
    return "OK"

