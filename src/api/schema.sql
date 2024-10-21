
CREATE TABLE potion_options (
    id integer PRIMARY KEY,
    name text,
    potion_type int ARRAY[4],
    red int,
    green int,
    blue int,
    dark int,
    quantity int,
    price int
);

CREATE TABLE carts (
    cart_id integer PRIMARY KEY,
    name text,
);

CREATE TABLE customer_cart (
    customer_id integer PRIMARY KEY,
    cart_id integer,
    potion_name text,
    quantity text,
);


ALTER TABLE global_inventory
ADD COLUMN num_dark_ml INTEGER DEFAULT 0;

INSERT INTO potion_options (id, name, potion_type, red, green, blue, dark, quantity, price) VALUES
 (1, 'Gold Potion', '{54, 46, 0, 0}', 54, 47, 0, 0, 0, 80),
 (2, 'Christmas Potion', '{33, 33, 33,0}', 33, 33, 34, 0, 0, 80),
 (3, 'Earth Potion', '{50, 30, 20, 0}', 50, 30, 20, 0, 0, 60),
 (4, 'Purple Potion', '{50, 0, 50,0}', 50, 0, 50, 0, 0, 70),
 (5, 'Red Potion', '{100, 0, 0,0}', 100, 0, 0, 0, 0, 60),
 (6, 'Green Potion', '{0, 100, 0,0}', 0, 100, 0, 0, 0, 60);
