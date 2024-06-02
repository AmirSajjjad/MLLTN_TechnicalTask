# MLLTN_TechnicalTask

This project is a technical interview task for the "Malltina" company. The goal is to retrieve data for a given product ID from the "Amazon" site and return it to the user. Here are the steps:

1. If the data exists in the cache, return it to the user.
2. If the data is not in the cache, check the database (db).
3. If the data is not in the database, fetch it from the "Amazon" site, save it to the database and cache, and then return it to the user.

# URLs:
useing this api to check amazon products: "/products/amazon/{AMAZON-PRODUCT-CODE}"