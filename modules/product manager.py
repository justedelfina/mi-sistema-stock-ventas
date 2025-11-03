import json
from datetime import datetime




class ProductManager:
   def __init__(self, data_file="data/products.json"):
       self.data_file = data_file


   def add_product(self, product_data):
       """Agrega un nuevo producto"""
       products = self.load_products()
       product_data['id'] = len(products) + 1
       product_data['created_at'] = datetime.now().isoformat()
       products.append(product_data)
       return self.save_products(products)


   def load_products(self):
       """Carga todos los productos"""
       try:
           with open(self.data_file, 'r') as f:
               return json.load(f)
       except (FileNotFoundError, json.JSONDecodeError):
           return []


   def save_products(self, products):
       """Guarda los productos"""
       try:
           with open(self.data_file, 'w') as f:
               json.dump(products, f, indent=2)
           return True
       except Exception:
           return False


   def get_product(self, product_id):
       """Obtiene un producto por ID"""
       products = self.load_products()
       return next((p for p in products if p['id'] == product_id), None)


   def update_product(self, product_id, updated_data):
       """Actualiza un producto"""
       products = self.load_products()
       for i, product in enumerate(products):
           if product['id'] == product_id:
               products[i].update(updated_data)
               return self.save_products(products)
       return False

