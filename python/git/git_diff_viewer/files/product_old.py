#!/usr/bin/env python3
"""
Product Management System - Old Version
Handles basic product operations
"""

class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
    
    def calculate_total_value(self):
        """Calculate total value of product inventory"""
        return self.price * self.quantity
    
    def display_info(self):
        """Display product information"""
        print(f"Product: {self.name}")
        print(f"Price: ${self.price:.2f}")
        print(f"Quantity: {self.quantity}")
        print(f"Total Value: ${self.calculate_total_value():.2f}")
    
    def apply_discount(self, percentage):
        """Apply discount to product price"""
        if 0 <= percentage <= 100:
            self.price = self.price * (1 - percentage/100)
            return True
        return False

def load_products_from_file(filename):
    """Load products from text file"""
    products = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                data = line.strip().split(',')
                if len(data) == 3:
                    name = data[0]
                    price = float(data[1])
                    quantity = int(data[2])
                    products.append(Product(name, price, quantity))
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
    return products

# Main execution
if __name__ == "__main__":
    # Sample products
    products = [
        Product("Laptop", 999.99, 5),
        Product("Mouse", 25.50, 10),
        Product("Keyboard", 75.00, 8)
    ]
    
    print("=== PRODUCT INVENTORY ===")
    for product in products:
        product.display_info()
        print("-" * 20)

"""
2025-10-04_1355hr_46sec
"""