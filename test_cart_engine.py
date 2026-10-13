from cart_engine import VirtualCartEngine


def test_register_shopper():
    cart_engine = VirtualCartEngine()
    cart_engine.register_shopper("shopper_1")
    assert "shopper_1" in cart_engine.carts
    assert cart_engine.carts["shopper_1"] == {"items": {}, "checked_out": False}


def test_add_item():
    cart_engine = VirtualCartEngine()
    cart_engine.add_item("shopper_1", "shelf_soda")
    assert cart_engine.carts["shopper_1"]["items"]["shelf_soda"] == 1


def test_generate_receipt_with_items():
    cart_engine = VirtualCartEngine()
    cart_engine.add_item("shopper_1", "shelf_soda")
    receipt = cart_engine.generate_receipt("shopper_1")
    assert receipt == {"shelf_soda": 1}


def test_generate_receipt_empty_cart():
    cart_engine = VirtualCartEngine()
    receipt = cart_engine.generate_receipt("shopper_1")
    assert receipt is None


def test_add_item_existing_shopper():
    cart_engine = VirtualCartEngine()
    cart_engine.add_item("shopper_1", "shelf_soda")
    cart_engine.add_item("shopper_1", "shelf_water")
    assert cart_engine.carts["shopper_1"]["items"]["shelf_water"] == 1
    assert cart_engine.carts["shopper_1"]["items"]["shelf_soda"] == 1