from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
from datetime import datetime
from sqlalchemy import select, and_, cast, Numeric, func, distinct


metadata_obj = sqlalchemy.MetaData()
customer_cart = sqlalchemy.Table("customer_cart", metadata_obj, autoload_with=db.engine)
customers = sqlalchemy.Table("customers", metadata_obj, autoload_with=db.engine)
global_inventory = sqlalchemy.Table("global_inventory", metadata_obj, autoload_with=db.engine)
potion_inventory = sqlalchemy.Table("potion_inventory", metadata_obj, autoload_with=db.engine)
potion_options = sqlalchemy.Table("potion_options", metadata_obj, autoload_with=db.engine)
test = sqlalchemy.Table("test", metadata_obj, autoload_with=db.engine)




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
    
    base_query = (
        select (
            customer_cart.c.item_sku,
            customers.c.name,
            func.sum(func.cast(customer_cart.c.quantity, Numeric) * func.cast(potion_options.c.price, Numeric)).label("total_price"),
            test.c.timestamp
            
        )
        .select_from(customer_cart)  
        .join(potion_options, potion_options.c.sku == customer_cart.c.item_sku)
        .join(test, test.c.potion_type == potion_options.c.potion_type)
        .join(customers, customers.c.customer_id == customer_cart.c.customer_id)
        .group_by(customer_cart.c.item_sku, customers.c.name, test.c.timestamp, customer_cart.c.quantity, potion_options.c.price)
        
        
    )

    with db.engine.begin() as connection:
        res = connection.execute(base_query).fetchall()
        print(res)


    if customer_name != "" and potion_sku != "":
        base_query = base_query.where(and_(
                customers.c.name == customer_name,
                customer_cart.c.item_sku == potion_sku
                ))
    elif customer_name != "" and potion_sku == "":
        with db.engine.begin() as connection:
            res = connection.execute(base_query).fetchall()
            print(res)
        base_query = base_query.where(customers.c.name == customer_name)
    
    elif customer_name == "" and potion_sku != "": 
        base_query = base_query.where(customer_cart.c.item_sku == potion_sku)
      
   

    # Sorting logic with match-case structure
    match sort_col:
        case search_sort_options.timestamp:
            sort_column = test.c.timestamp
          

        case search_sort_options.customer_name:
            sort_column = customers.c.name
           

        case search_sort_options.item_sku:
            sort_column = customer_cart.c.item_sku
           

        case search_sort_options.line_item_total:
            sort_column = customer_cart.c.quantity * potion_options.c.price
        

        case _:
            sort_column = test.c.timestamp  # Default sort by timestamp if no match
          

  

    if search_page != "":
        if sort_order == "asc":
            # For ascending order pagination
            base_query = base_query.where(sort_column > search_page)
        elif sort_order == "desc":
            # For descending order pagination
            base_query = base_query.where(sort_column < search_page)
 

    # Handle sorting order with match-case
    if sort_order == "asc":
        base_query = base_query.order_by(sort_column.asc())
    else:  # Default to descending order
        base_query = base_query.order_by(sort_column.desc())
    


    #base_query = base_query.limit(5)  # Limit results to 5 per page
    with db.engine.begin() as connection:
        res = connection.execute(base_query).fetchall()
    
    num_results = len(res)
    res = res[:5]
    results = []
    print(res)
    
    match sort_col:
        case search_sort_options.timestamp:
            search_token_next =  res[-1][3]
            search_token_prev = res[0][3]

        case search_sort_options.customer_name:
            search_token_next =  res[-1][1]
            search_token_prev = res[0][1]

        case search_sort_options.item_sku:
            search_token_next =  res[-1][0]
            search_token_prev = res[0][0]

        case search_sort_options.line_item_total:
            search_token_next =  res[-1].total_price
            search_token_prev = res[0].total_price

        case _:
            search_token_next =  res[-1][2]
            search_token_prev = res[0][2]
    
    for row in res:
        results.append({
            "line_item_id": row.item_sku,  
            "customer_name": row.name,
            "total_price": int(row.total_price),  # Cast to float for easier consumption
            "timestamp": row.timestamp
        })
    
    

    next_token = None
    previous_token = None

    if num_results > 5:  # If we have 5 results, there might be more data
        next_token = search_token_next  # For ascending order, use the last result's timestamp as the next token
        previous_token = search_token_prev  # Use the first result's timestamp as the previous token
        
    elif num_results <= 5:
        next_token = ""
        previous_token = ""

    print("neXT: ", next_token)
    print("prev: ", previous_token)
    return {
        "next": next_token,  # Timestamp of the last item in this set, used for the next page
        "previous": previous_token,  # Timestamp of the first item in this set, used for the previous page
        "results": results
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
    

    """Create a cart for a customer, adding the customer if they don't exist."""
    with db.engine.begin() as connection:

        check_customer = connection.execute(
            sqlalchemy.text("SELECT customer_id FROM customers WHERE name = :name"), {"name": new_cart.customer_name}).fetchone()

        # If the customer does not exist, insert them
        if check_customer is None:
            customer_id = connection.execute(
                sqlalchemy.text(
                    "INSERT INTO customers (name, character_class, level) VALUES (:name, :char_class, :level) RETURNING customer_id"),
                {
                    "name": new_cart.customer_name,
                    "char_class": new_cart.character_class,
                    "level": new_cart.level
                }).fetchone()[0]

        # Retrieve existing customer ID
        else:
            customer_id = check_customer[0]  
       

        # Insert a new row into the customer_cart table
        cart_id = connection.execute(
            sqlalchemy.text("INSERT INTO customer_cart (customer_id) VALUES (:customer_id) RETURNING cart_id"),
            {"customer_id": customer_id}).fetchone()[0]

    return {"cart_id": cart_id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        check_cart = connection.execute(sqlalchemy.text("SELECT item_sku FROM customer_cart WHERE cart_id = :cart_id"), {"cart_id": cart_id}).fetchone()
        customer_id = connection.execute(sqlalchemy.text("SELECT customer_id FROM customer_cart WHERE cart_id = :cart_id"), {"cart_id": cart_id}).fetchone()
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
        order = connection.execute(sqlalchemy.text("SELECT potion_options.potion_type, customer_cart.quantity, price "
                                                   "FROM potion_options INNER JOIN customer_cart ON potion_options.sku = customer_cart.item_sku "
                                                   "WHERE cart_id = :cart_id"), {"cart_id": cart_id}).fetchall()
        print("order: ", order)
        for i in range(len(order)):
            current_datetime = datetime.datetime.now()
            print("ORDER: ", order[i][1])
            print("ORDER 2: ", order[i][2])
            total_potions_bought += int(order[i][1])
            total_gold_paid += (int(order[i][1]) * order[i][2])
            print("LOOK AT THIS quantity ",  order[i][1])
            connection.execute(sqlalchemy.text("INSERT INTO potion_inventory (potion_type, quantity, timestamp, cart_id) VALUES (:potion_type, :quantity, :timestamp, :cart_id)"), 
                               {"potion_type": order[i][0], "quantity": -int(order[i][1]), "timestamp": current_datetime, "cart_id": cart_id})            
        connection.execute(sqlalchemy.text("INSERT INTO global_inventory (gold) VALUES (:gold)"),
                                           {"gold": total_gold_paid})
  

    return {
        "total_potions_bought": total_potions_bought,
        "total_gold_paid":  total_gold_paid
        }

  

