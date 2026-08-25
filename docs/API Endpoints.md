# API Endpoints — Bubble Tea Shop
 
Format: `METHOD /path → what it does`
 
## Auth
```
POST   /auth/login            → log in with username + password, returns a token
```
 
## Ingredients
```
GET    /ingredients           → list all ingredients (with current stock, derived)
GET    /ingredients/{id}      → get one ingredient
POST   /ingredients           → create an ingredient
PUT    /ingredients/{id}      → update an ingredient
DELETE /ingredients/{id}      → delete an ingredient (blocked if used in a recipe)
```
 
## Recipes
```
GET    /recipes               → list all recipes (with their ingredients)
GET    /recipes/{id}          → get one recipe
POST   /recipes               → create a recipe, including its ingredient list
PUT    /recipes/{id}          → update a recipe and/or its ingredients
DELETE /recipes/{id}          → delete a recipe (blocked if it has past orders — see open question)
```
 
## Orders (staff-recorded sales)
```
POST   /orders                → record a sale — creates order + items, deducts stock
GET    /orders                → list all orders
GET    /orders/{id}           → get one order with its items
```
 
## Guest orders
```
POST   /guest-orders          → same as POST /orders, but no auth required
GET    /menu                  → public list of recipes, for the guest-facing screen
```
 
## Stock movements
```
GET    /stock-movements                    → list all movements (filter by ingredient_id, reason)
POST   /stock-movements/restock            → record a restock (positive movement + cost)
POST   /stock-movements/adjustment         → manual adjustment (e.g. wastage)
```
 
## Consumption rate
```
GET    /ingredients/{id}/consumption-rate  → daily usage rate + estimated days until stockout
GET    /ingredients/low-stock              → list ingredients projected to run low soon
```
 
## Dashboard
```
GET    /dashboard?period=1|7|30            → income/outcome summary for the period
```