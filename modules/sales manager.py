import json
from datetime import datetime




class SalesManager:
   def __init__(self, data_file="data/sales.json"):
       self.data_file = data_file


   def record_sale(self, products, total_amount):
       """Registra una nueva venta"""
       sales = self.load_sales()


       sale_data = {
           "id": len(sales) + 1,
           "date": datetime.now().isoformat(),
           "products": products,
           "total": total_amount,
           "items_count": sum(item['quantity'] for item in products)
       }


       sales.append(sale_data)
       return self.save_sales(sales), sale_data


   def load_sales(self):
       """Carga todas las ventas"""
       try:
           with open(self.data_file, 'r') as f:
               return json.load(f)
       except (FileNotFoundError, json.JSONDecodeError):
           return []


   def save_sales(self, sales):
       """Guarda las ventas"""
       try:
           with open(self.data_file, 'w') as f:
               json.dump(sales, f, indent=2)
           return True
       except Exception:
           return False


   def get_daily_sales(self, date=None):
       """Obtiene ventas del día"""
       sales = self.load_sales()
       if date is None:
           date = datetime.now().date()


       daily_sales = [s for s in sales if datetime.fromisoformat(s['date']).date() == date]
       return daily_sales


   def get_monthly_sales(self, year=None, month=None):
       """Obtiene ventas del mes"""
       sales = self.load_sales()
       if year is None:
           year = datetime.now().year
       if month is None:
           month = datetime.now().month


       monthly_sales = [
           s for s in sales
           if datetime.fromisoformat(s['date']).year == year and
              datetime.fromisoformat(s['date']).month == month
       ]
       return monthly_sales
