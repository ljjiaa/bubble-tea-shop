```mermaid
C4Context
    title System Context - Bubble Tea Shop
    Person(customer, "Customer", "Browses menu, places orders (incl. guest)")
    Person(manager, "Manager / Owner", "Manages recipes, inventory, sales")
    System(shop, "Bubble Tea Shop System", "Ordering + shop management")
    System_Ext(supplier, "Supplier API", "Restocking")
    Rel(customer, shop, "Places orders")
    Rel(manager, shop, "Manages shop")
    Rel(shop, supplier, "Restocks ingredients")
```
