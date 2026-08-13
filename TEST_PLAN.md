# Test Plan

## Project Overview

The project implements a virtual cart system that tracks items added by shoppers in a simulated store environment. The system detects hand movements via a camera, allowing users to add items to their cart from shelves and check out by exiting the area. The key components include a `VirtualCartEngine` that manages the cart logic and a motion-based interface in `main.py` that leverages computer vision techniques.

## Selected Test Types

- Unit tests
- Edge-case tests
- Exception/Error tests
- Integration tests

## Test Cases

### TC001 - Register a New Shopper

- **Source File:** cart_engine.py
- **Function/Class/Method:** register_shopper
- **Test Type:** Unit test
- **Objective:** Verify that a new shopper can be registered.
- **Preconditions:** The `VirtualCartEngine` is instantiated.
- **Input / Test Data:** shopper_id = "shopper_1"
- **Expected Result:** The `carts` dictionary contains an entry for "shopper_1" with an empty items list and checked_out set to False.
- **Reason for Testing:** To ensure that the method correctly initializes a cart for a new shopper.
- **Priority:** High

### TC002 - Add Item to Shopper's Cart

- **Source File:** cart_engine.py
- **Function/Class/Method:** add_item
- **Test Type:** Unit test
- **Objective:** Validate that adding an item increments the item count for the shopper.
- **Preconditions:** A shopper registered using `register_shopper`.
- **Input / Test Data:** shopper_id = "shopper_1", product_key = "shelf_soda"
- **Expected Result:** The item count for "shelf_soda" is incremented to 1 in the shopper's cart.
- **Reason for Testing:** To confirm that the method correctly updates the item count.
- **Priority:** High

### TC003 - Generate Receipt with Items

- **Source File:** cart_engine.py
- **Function/Class/Method:** generate_receipt
- **Test Type:** Unit test
- **Objective:** Ensure that a receipt is generated correctly when there are items in the cart.
- **Preconditions:** At least one item has been added to the shopper's cart.
- **Input / Test Data:** shopper_id = "shopper_1"
- **Expected Result:** The method returns a dictionary of items in the cart and displays the receipt.
- **Reason for Testing:** To verify that receipts are generated correctly when there are items in the cart.
- **Priority:** High

### TC004 - Generate Receipt with Empty Cart

- **Source File:** cart_engine.py
- **Function/Class/Method:** generate_receipt
- **Test Type:** Edge-case test
- **Objective:** Validate that no receipt is generated when the cart is empty.
- **Preconditions:** No items have been added to the shopper's cart.
- **Input / Test Data:** shopper_id = "shopper_1"
- **Expected Result:** The method returns None.
- **Reason for Testing:** To ensure the method handles empty carts as expected.
- **Priority:** Medium

### TC005 - Add Item after Shopper Already Exists

- **Source File:** cart_engine.py
- **Function/Class/Method:** add_item
- **Test Type:** Unit test
- **Objective:** Test that the method correctly handles adding an item to an existing shopper's cart.
- **Preconditions:** A shopper is already registered with items in their cart.
- **Input / Test Data:** shopper_id = "shopper_1", product_key = "shelf_water"
- **Expected Result:** The count for "shelf_water" is added to the existing items in the cart.
- **Reason for Testing:** To ensure that the method does not overwrite existing shoppers and can append to their carts.
- **Priority:** High

### TC006 - Invalid Camera Access Handling

- **Source File:** main.py
- **Function/Class/Method:** run_camera
- **Test Type:** Exception/Error test
- **Objective:** Ensure that the program handles camera access failures gracefully.
- **Preconditions:** Camera access fails (simulated).
- **Input / Test Data:** N/A
- **Expected Result:** The message "Failed to access camera." is printed, and the program exits.
- **Reason for Testing:** To verify that appropriate error handling is in place for camera issues.
- **Priority:** Medium

### TC007 - Detect Hand Motion Below the Threshold

- **Source File:** main.py
- **Function/Class/Method:** run_camera
- **Test Type:** Edge-case test
- **Objective:** Validate that small hand movements below the contour area threshold do not trigger item addition.
- **Preconditions:** Hand movements detected below the contour area threshold of 1200.
- **Input / Test Data:** Contours detected with areas < 1200.
- **Expected Result:** No items are added to the cart, and no messages are printed.
- **Reason for Testing:** To confirm the system accurately ignores small movements.
- **Priority:** Medium

### TC008 - Shelf Interaction Timeout

- **Source File:** main.py
- **Function/Class/Method:** run_camera
- **Test Type:** Integration test
- **Objective:** Verify that cooldowns prevent multiple item additions for the same shelf interaction within a given period.
- **Preconditions:** Hand is detected interacting with a shelf.
- **Input / Test Data:** shelf_id = "shelf_chips"
- **Expected Result:** Item is added only once within the cooldown timeframe; subsequent attempts do not add items.
- **Reason for Testing:** To ensure the cooldown feature works correctly and prevents spam item additions.
- **Priority:** High

## Test Coverage Areas

- Registering a new shopper
- Adding items to a shopper's cart
- Generating receipts for shoppers
- Handling situations with empty carts
- Ensuring hand movements are processed correctly
- Managing cooldowns for shelf interactions
- Error handling for camera access

## Test Environment / Dependencies

- A mock camera system or simulator to test `run_camera` functionality without actual camera input.
- Mocked data for shelf regions and product lists to test cart interactions.
- Simulated inputs for motion detection during tests.