-- mm-shopping-cart/db/mm-shopping-cart.sql

-- Create the marketmaster database
CREATE DATABASE marketmaster;

\connect marketmaster;


-- Create the shoppingcart table
CREATE TABLE IF NOT EXISTS shoppingcart (
    id SERIAL PRIMARY KEY,
    customercpf VARCHAR(11) NOT NULL, -- This is the customer's CPF, external ref to the customer service
    status BOOLEAN NOT NULL DEFAULT FALSE, -- FALSE for active, TRUE for purchased
    datecreated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create the shoppingcart_items table
CREATE TABLE IF NOT EXISTS shoppingcart_items (
    id SERIAL PRIMARY KEY,
    cartid INTEGER NOT NULL REFERENCES shoppingcart(id) ON DELETE CASCADE,
    productitemid INTEGER NOT NULL, -- This references an ID in the mm-inventory service
    quantity INTEGER NOT NULL
);

-- Indexes to improve query performance
CREATE INDEX IF NOT EXISTS idx_cart_productitems_cartid ON shoppingcart_items(cartid);
CREATE INDEX IF NOT EXISTS idx_shoppingcart_customerid ON shoppingcart(customercpf);
