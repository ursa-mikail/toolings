#!/usr/bin/env python3
"""
Product Management System - Enhanced Version
Handles product operations with additional features and validation
"""

class Product:
    def __init__(self, name, price, quantity, category="General", sku=None):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.category = category
        self.sku = sku or f"SKU-{name.upper().replace(' ', '-')}"
        self._validate_attributes()
    
    def _validate_attributes(self):
        """Validate product attributes"""
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if not self.name.strip():
            raise ValueError("Product name cannot be empty")
    
    def calculate_total_value(self):
        """Calculate total value of product inventory with tax consideration"""
        BASE_TAX_RATE = 1.08  # 8% tax
        return self.price * self.quantity * BASE_TAX_RATE
    
    def display_info(self, include_tax=False):
        """Display product information with optional tax details"""
        print(f"Product: {self.name}")
        print(f"SKU: {self.sku}")
        print(f"Category: {self.category}")
        print(f"Price: ${self.price:.2f}")
        print(f"Quantity: {self.quantity}")
        
        if include_tax:
            total_with_tax = self.calculate_total_value()
            total_without_tax = self.price * self.quantity
            print(f"Subtotal: ${total_without_tax:.2f}")
            print(f"Total with Tax (8%): ${total_with_tax:.2f}")
        else:
            print(f"Total Value: ${self.calculate_total_value():.2f}")
    
    def apply_discount(self, percentage, discount_type="percentage"):
        """Apply discount to product price with different discount types"""
        if discount_type == "percentage":
            if 0 <= percentage <= 100:
                self.price = self.price * (1 - percentage/100)
                return True
        elif discount_type == "fixed":
            if 0 <= percentage <= self.price:
                self.price -= percentage
                return True
        return False
    
    def restock(self, additional_quantity):
        """Add more quantity to existing product"""
        if additional_quantity > 0:
            self.quantity += additional_quantity
            return True
        return False
    
    def is_low_stock(self, threshold=5):
        """Check if product is running low on stock"""
        return self.quantity < threshold

def load_products_from_file(filename):
    """Load products from CSV file with enhanced error handling"""
    products = []
    try:
        with open(filename, 'r') as file:
            headers = file.readline().strip().split(',')
            for line_num, line in enumerate(file, 2):
                data = line.strip().split(',')
                if len(data) >= 3:
                    name = data[0].strip()
                    price = float(data[1])
                    quantity = int(data[2])
                    category = data[3].strip() if len(data) > 3 else "General"
                    sku = data[4].strip() if len(data) > 4 else None
                    
                    products.append(Product(name, price, quantity, category, sku))
                else:
                    print(f"Warning: Invalid data on line {line_num}")
    
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
    except ValueError as e:
        print(f"Error: Invalid data format - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return products

def generate_inventory_report(products):
    """Generate a comprehensive inventory report"""
    total_value = sum(p.calculate_total_value() for p in products)
    low_stock_items = [p for p in products if p.is_low_stock()]
    
    print("=== ENHANCED PRODUCT INVENTORY REPORT ===")
    print(f"Total Products: {len(products)}")
    print(f"Total Inventory Value: ${total_value:.2f}")
    print(f"Low Stock Items: {len(low_stock_items)}")
    print("\n" + "=" * 50)
    
    for product in products:
        low_stock_indicator = " [LOW STOCK]" if product.is_low_stock() else ""
        print(f"{product.name}{low_stock_indicator}")
        product.display_info(include_tax=True)
        print("-" * 30)

# Main execution
if __name__ == "__main__":
    # Sample products with enhanced features
    products = [
        Product("Laptop", 999.99, 5, "Electronics", "SKU-LTP-001"),
        Product("Wireless Mouse", 25.50, 2, "Electronics"),
        Product("Mechanical Keyboard", 75.00, 8, "Electronics", "SKU-KBD-002"),
        Product("Desk Lamp", 45.00, 15, "Home Goods")
    ]
    
    generate_inventory_report(products)
    
    # Demonstrate new features
    print("\n=== DEMONSTRATING NEW FEATURES ===")
    sample_product = products[1]
    print(f"Before discount: ${sample_product.price:.2f}")
    sample_product.apply_discount(10)  # 10% discount
    print(f"After 10% discount: ${sample_product.price:.2f}")
    
    sample_product.restock(10)
    print(f"After restocking: {sample_product.quantity} units")

"""
# Basic diff
git diff --no-index ./files/product_old.py ./files/product_new.py

# Side-by-side diff
git diff --word-diff --no-index ./files/product_old.py ./files/product_new.py

# Colored diff with context
git diff --color --unified=10 ./files/product_old.py ./files/product_new.py

# See only the method signatures that changed
git diff --no-index -G  "def " ./files/product_old.py ./files/product_new.py

# to quit
[esc] wq 
"""