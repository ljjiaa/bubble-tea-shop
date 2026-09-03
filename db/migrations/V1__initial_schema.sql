-- Bubble Tea Shop - database schema
-- PostgreSQL 18

CREATE TABLE ingredients (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    unit VARCHAR(30) NOT NULL,
    reorder_threshold NUMERIC(10,2) NOT NULL DEFAULT 0
);


CREATE TABLE recipes (
    id     INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name   VARCHAR(120) NOT NULL UNIQUE,
    price  NUMERIC(10,2) NOT NULL CHECK (price >= 0)
);

-- Links recipes to the ingredients they use, with quantities
CREATE TABLE recipe_ingredients (
    id             INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recipe_id      INT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,      -- delete recipe, links go too
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT, -- block deleting an ingredient in use
    quantity_used  NUMERIC(10,2) NOT NULL CHECK (quantity_used > 0),
    UNIQUE (recipe_id, ingredient_id)  -- same ingredient can't appear twice in one recipe
);


-- Staff and (future) customer accounts
CREATE TABLE app_users (
    id             INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username       VARCHAR(100) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,   -- never store the raw password
    role           VARCHAR(20)  NOT NULL DEFAULT 'manager'
                   CHECK (role IN ('owner', 'manager', 'customer'))
);

-- One order. MVP orders are all guests, so customer_id is nullable.
CREATE TABLE orders (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     INT REFERENCES app_users(id) ON DELETE SET NULL,  -- keep the order if the user is deleted
    status          VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_method  VARCHAR(20) NOT NULL DEFAULT 'cash',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Line items on an order
CREATE TABLE order_items (
    id         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id   INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,     -- items die with the order
    recipe_id  INT NOT NULL REFERENCES recipes(id) ON DELETE RESTRICT,   -- block deleting a sold recipe
    quantity   INT NOT NULL CHECK (quantity > 0)
);

-- Every stock change, in or out. Single source of truth for stock levels.
CREATE TABLE stock_movements (
    id             INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    change_amount  NUMERIC(10,2) NOT NULL CHECK (change_amount <> 0),  -- + in, - out, never zero
    cost           NUMERIC(10,2) CHECK (cost >= 0),                    -- nullable: restocks only
    reason         VARCHAR(20) NOT NULL
                   CHECK (reason IN ('initial', 'restock', 'sale', 'wastage')),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);