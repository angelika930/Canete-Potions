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
    """ """
    global cart_index
    global cart_dict
    cart_index += 1
    cart_dict[cart_index] = []
    return {"cart_id": cart_index}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    global cart_index
    global cart_dict
    item = (item_sku, cart_item.quantity)
    cart_dict[cart_id].append(item)

    print(cart_dict)

    
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
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        price = connection.execute(sqlalchemy.text("SELECT price FROM potion_options"))
        sku_query = connection.execute(sqlalchemy.text("SELECT sku FROM potion_options"))

    price_list = [p[0] for p in price]
    sku_list = [s[0] for s in sku_query]
     
    global cart_dict
    for sku, quantity in cart_dict[cart_id]:

       
        with db.engine.begin() as connection:
            if sku == sku_list[0]:
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity - :total_potions WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1"), {"total_potions": quantity})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :total_gold"), {"total_gold": price_list[0]*quantity})
                total_gold_paid += price_list[0]*quantity

            elif sku == sku_list[1]:
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity - :total_potions WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 1"), {"total_potions": quantity})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :total_gold"), {"total_gold": price_list[1]*quantity})
                total_gold_paid += price_list[1]*quantity

            elif sku == sku_list[2]:
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity - :total_potions WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 2"), {"total_potions": quantity})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :total_gold"), {"total_gold": price_list[2]*quantity})
                total_gold_paid += price_list[2]*quantity

            elif sku == sku_list[3]:
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity - :total_potions WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 3"), {"total_potions": quantity})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :total_gold"), {"total_gold": price_list[3]*quantity})
                total_gold_paid += price_list[3]*quantity
            
            elif sku == sku_list[4]:
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity - :total_potions WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 4"), {"total_potions": quantity})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :total_gold"), {"total_gold": price_list[4]*quantity})
                total_gold_paid += price_list[4]*quantity
            
            elif sku == sku_list[5]:
                connection.execute(sqlalchemy.text("UPDATE potion_options SET quantity = quantity - :total_potions WHERE id = (SELECT id FROM potion_options ORDER BY id LIMIT 1 OFFSET 5"), {"total_potions": quantity})
                connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :total_gold"), {"total_gold": price_list[5]*quantity})
                total_gold_paid += price_list[5]*quantity

            total_potions_bought += quantity


        print(sku)
    return {
        "total_potions_bought": total_potions_bought,
        "total_gold_paid":  total_gold_paid
        }

    #print("CART CHECKOUT STRING: ", cart_checkout.payment)
    #print("TEST?????: ", int(cart_checkout.payment))


