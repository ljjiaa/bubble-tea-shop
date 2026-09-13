-- Link stock movements to the order that caused them (nullable — restocks/manual adjustments have no order)
ALTER TABLE stock_movements ADD COLUMN order_id INT REFERENCES orders(id) ON DELETE SET NULL;

-- Distinguish how stock came in/out: from a supplier, or a manual correction
ALTER TABLE stock_movements ADD COLUMN type VARCHAR(20) CHECK (type IN ('supplier', 'manual'));

-- Cost per unit, for profit-per-cup calculation
ALTER TABLE ingredients ADD COLUMN cost_per_unit NUMERIC(10,2) CHECK (cost_per_unit >= 0);

-- Daily opening/closing stock snapshot per ingredient
CREATE TABLE stock_snapshots (
    id             INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingredient_id  INT NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    snapshot_date  DATE NOT NULL,
    opening_qty    NUMERIC(10,2) NOT NULL,
    closing_qty    NUMERIC(10,2) NOT NULL,
    UNIQUE (ingredient_id, snapshot_date)
);