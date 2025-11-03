import json
from datetime import datetime




class StockManager:
   def __init__(self, data_file="data/stock.json"):
       self.data_file = data_file


   def set_stock(self, product_id, quantity):
       """Establece el stock de un producto"""
       stock_data = self.load_stock()


       stock_data[str(product_id)] = {
           'quantity': quantity,
           'last_updated': datetime.now().isoformat()
       }


       return self.save_stock(stock_data)


   def update_stock(self, product_id, quantity_change):
       """Actualiza el stock (suma o resta)"""
       stock_data = self.load_stock()


       current_quantity = stock_data.get(str(product_id), {}).get('quantity', 0)
       new_quantity = max(0, current_quantity + quantity_change)


       stock_data[str(product_id)] = {
           'quantity': new_quantity,
           'last_updated': datetime.now().isoformat()
       }


       return self.save_stock(stock_data)


   def load_stock(self):
       """Carga todos los datos de stock"""
       try:
           with open(self.data_file, 'r') as f:
               return json.load(f)
       except (FileNotFoundError, json.JSONDecodeError):
           return {}


   def save_stock(self, stock_data):
       """Guarda los datos de stock"""
       try:
           with open(self.data_file, 'w') as f:
               json.dump(stock_data, f, indent=2)
           return True
       except Exception:
           return False


   def get_stock_level(self, product_id):
       """Obtiene el nivel de stock de un producto"""
       stock_data = self.load_stock()
       return stock_data.get(str(product_id), {}).get('quantity', 0)


   def get_all_stock(self, products):
       """Obtiene todo el stock con información de productos"""
       stock_data = self.load_stock()
       stock_with_products = []


       for product in products:
           product_id = str(product['id'])
           stock_info = stock_data.get(product_id, {})


           stock_with_products.append({
               'id': product['id'],
               'name': product['name'],
               'category': product['category'],
               'price': product['price'],
               'stock': stock_info.get('quantity', 0),
               'last_updated': stock_info.get('last_updated', 'Nunca')
           })


       return stock_with_products
