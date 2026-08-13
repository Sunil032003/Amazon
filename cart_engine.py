# cart_engine.py

class VirtualCartEngine:
    def __init__(self):
        # Format: { shopper_id: {"items": {product_key: count}, "checked_out": Bool} }
        self.carts = {}

    def register_shopper(self, shopper_id):
        if shopper_id not in self.carts:
            self.carts[shopper_id] = {"items": {}, "checked_out": False}

    def add_item(self, shopper_id, product_key):
        self.register_shopper(shopper_id)
        current_count = self.carts[shopper_id]["items"].get(product_key, 0)
        self.carts[shopper_id]["items"][product_key] = current_count + 1

    def generate_receipt(self, shopper_id):
        # Register if not present
        self.register_shopper(shopper_id)
        
        # Don't generate empty receipts
        cart_items = self.carts[shopper_id]["items"]
        if not cart_items:
            return None

        print(f"\n==================================")
        print(f"   RECEIPT FOR SHOPPER #{shopper_id}")
        print(f"==================================")
        for item, qty in cart_items.items():
            print(f" - {item} x{qty}")
        print(f"==================================\n")

        # RESET CART FOR NEXT TRIP
        self.carts[shopper_id] = {"items": {}, "checked_out": False}
        return cart_items