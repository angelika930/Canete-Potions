CREATE TABLE customer_carts (
    id cart_id generated always as identity,
    customer_name text
    
);

CREATE TABLE cart_items (
    id potion_id generated always as identity,
    potion_items: INT[][],
    total_price: int
);


CREATE TABLE potions (
    id potion_id generated always as identity,
    potion_type INT[],
    quantity int,
    price int
);


