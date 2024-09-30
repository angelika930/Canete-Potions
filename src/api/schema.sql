CREATE TABLE customer_carts (
    cart_id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL
    
);

CREATE TABLE cart_items (
    potion_id PRIMARY KEY,
    potion_items INT[][],
    total_price int NOT NULL
);

CREATE TABLE potions (
    potion_id PRIMARY KEY,
    potion_type INT[],
    quantity int NOT NULL,
    price int NOT NULL
);


