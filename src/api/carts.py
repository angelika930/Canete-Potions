from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

#with db.engine.begin() as connection:
#        result = connection.execute(sqlalchemy.text(sql_to_execute))

cart_index = 0
cart_dict = {}


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """


    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int
    

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return {
        "success": True
        }


@router.post("/")
def create_cart(new_cart: Customer):
    """ 
    past_customer = []
    with db.engine.begin() as connection:
        past_customer = connection.execute(sqlalchemy.text("SELECT customer_id, name FROM customers "), {"name": new_cart.customer_name}).fetchall()
        check_customer = connection.execute(sqlalchemy.text("SELECT customer_id FROM customers WHERE name = :name"), {"name": new_cart.customer_name}).fetchall()

        print("what is in past_customer: ", past_customer)
        #For new customers, must be added in customers table first
        if past_customer == []:
            new_id = connection.execute(sqlalchemy.text("INSERT INTO customers(name, character_class, level) VALUES(:name, :char_class, :level) RETURNING customer_id"), {"name": new_cart.customer_name, "char_class": new_cart.character_class, "level": new_cart.level}).fetchone()
            new_id = 1
        
        elif check_customer == []:
            new_id = connection.execute(sqlalchemy.text("INSERT INTO customers(name, character_class, level) VALUES(:name, :char_class, :level) RETURNING customer_id"), {"name": new_cart.customer_name, "char_class": new_cart.character_class, "level": new_cart.level}).fetchone()[0]

       
        #For past customers, insert a new row
        else:
            new_id = connection.execute(sqlalchemy.text("INSERT INTO customer_cart (customer_id) VALUES (:customer_id) RETURNING customer_id"), {"customer_id": past_customer[0][0]}).fetchone()[0]

        
    with db.engine.begin() as connection:
    
        #insert new row into customer_cart table for new customers
        if check_customer == []:
            connection.execute(sqlalchemy.text("INSERT INTO customer_cart (customer_id) VALUES (:customer_id)"), {"customer_id": new_id})
  
    return {"cart_id": new_id}
    """

    """Create a cart for a customer, adding the customer if they don't exist."""
    with db.engine.begin() as connection:
        # Check if the customer exists
        max_cart_id = connection.execute(
            sqlalchemy.text("SELECT COALESCE(MAX(cart_id), 0) + 1 FROM customer_cart")
            ).scalar()
       

        check_customer = connection.execute(
            sqlalchemy.text("SELECT customer_id FROM customers WHERE name = :name"),
            {"name": new_cart.customer_name}
        ).fetchone()

        # If the customer does not exist, insert them
        if check_customer is None:
            new_id = connection.execute(
                sqlalchemy.text(
                    "INSERT INTO customers (name, character_class, level) VALUES (:name, :char_class, :level) RETURNING customer_id"
                ),
                {
                    "name": new_cart.customer_name,
                    "char_class": new_cart.character_class,
                    "level": new_cart.level
                }
            ).fetchone()[0]

        # Retrieve existing customer ID
        else:
            new_id = check_customer[0]  

        # Insert a new row into the customer_cart table
        cart_id = connection.execute(
            sqlalchemy.text("INSERT INTO customer_cart (customer_id, cart_id) VALUES (:customer_id, :cart_id) RETURNING cart_id"),
            {"customer_id": new_id, "cart_id": max_cart_id}
        ).fetchone()[0]

    return {"cart_id": cart_id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        check_cart = connection.execute(sqlalchemy.text("SELECT item_sku FROM customer_cart WHERE cart_id = :cart_id"), {"cart_id": cart_id}).fetchone()
        customer_id = connection.execute(sqlalchemy.text("SELECT customer_id FROM customer_cart WHERE cart_id = :cart_id"), {"cart_id": cart_id}).fetchone()
        print("CHECK CART: ", check_cart)
        if check_cart == (None,):
            with db.engine.begin() as connection:
                connection.execute(sqlalchemy.text("UPDATE customer_cart SET item_sku = :item_sku, quantity = :quantity WHERE customer_id = :customer_id AND cart_id = :cart_id"), {"item_sku": item_sku, "quantity": cart_item.quantity, "customer_id": customer_id[0], "cart_id": cart_id})
        
        else:
           connection.execute(sqlalchemy.text("INSERT INTO customer_cart (customer_id, cart_id, quantity, item_sku) VALUES (:customer_id,  :cart_id, :quantity, :item_sku)"), {"customer_id": customer_id[0],  "cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku})

    
    return {
    "success": "boolean"
    }


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    total_potions_bought = 0
    total_gold_paid = 0

    with db.engine.begin() as connection:
        order = connection.execute(sqlalchemy.text("SELECT potion_options.sku, customer_cart.quantity, price FROM potion_options JOIN customer_cart ON potion_options.sku = customer_cart.item_sku WHERE cart_id = :cart_id"), {"cart_id": cart_id}).fetchall()
        print("order: ", order)
        for i in range(len(order)):
            total_potions_bought += int(order[i][1])
            total_gold_paid += (int(order[i][1]) * order[i][2])
            connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity - :potions WHERE sku = :item_sku"), {"potions": int(order[i][1]), "item_sku": order[i][0]})
            
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :yield"), {"yield": total_gold_paid})
  

    return {
        "total_potions_bought": total_potions_bought,
        "total_gold_paid":  total_gold_paid
        }

    #print("CART CHECKOUT STRING: ", cart_checkout.payment)
    #print("TEST?????: ", int(cart_checkout.payment))


