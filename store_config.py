# store_config.py

PRODUCTS = {
    "shelf_soda": "Soda Can ($1.50)",
    "shelf_water": "Water Bottle ($1.00)",
    "shelf_chips": "Chip Bag ($2.00)",
    "shelf_chocolate": "Chocolate Bar ($1.25)"
}

# Adjusted regions at the top of a standard 640x480 frame
SHELF_ROIS = {
    "shelf_soda": (20, 20, 150, 160),
    "shelf_water": (170, 20, 300, 160),
    "shelf_chips": (320, 20, 450, 160),
    "shelf_chocolate": (470, 20, 600, 160),
}

# Exit line near the bottom quarter
EXIT_LINE_Y = 380