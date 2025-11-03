import pandas as pd
from datetime import datetime, timedelta




class ReportGenerator:
   def __init__(self, sales_manager, product_manager, stock_manager):
       self.sales_manager = sales_manager
       self.product_manager = product_manager
       self.stock_manager = stock_manager


   def generate_sales_report(self, start_date=None, end_date=None):
       """Genera reporte de ventas para un período"""
       sales = self.sales_manager.load_sales()


       if not sales:
           return None


       sales_df = pd.DataFrame(sales)
       sales_df['date'] = pd.to_datetime(sales_df['date'])


       if start_date and end_date:
           mask = (sales_df['date'] >= start_date) & (sales_df['date'] <= end_date)
           sales_df = sales_df.loc[mask]


       return sales_df


   def generate_stock_report(self):
       """Genera reporte de stock"""
       products = self.product_manager.load_products()
       stock_data = self.stock_manager.load_stock()


       stock_report = []
       for product in products:
           product_id = str(product['id'])
           stock_info = stock_data.get(product_id, {})
