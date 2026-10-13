import pytest
from store_config import PRODUCTS, SHELF_ROIS, EXIT_LINE_Y


def test_products_mapping():
    assert "shelf_soda" in PRODUCTS
    assert "shelf_water" in PRODUCTS
    assert "shelf_chips" in PRODUCTS
    assert "shelf_chocolate" in PRODUCTS
    assert len(PRODUCTS) == 4


def test_shelf_rois_match_products():
    assert set(SHELF_ROIS.keys()) == set(PRODUCTS.keys())


def test_shelf_rois_valid_coordinates():
    for shelf_id, (x1, y1, x2, y2) in SHELF_ROIS.items():
        assert x1 < x2, f"Shelf {shelf_id} has invalid width: x1={x1}, x2={x2}"
        assert y1 < y2, f"Shelf {shelf_id} has invalid height: y1={y1}, y2={y2}"
        assert x1 >= 0 and y1 >= 0, f"Shelf {shelf_id} coordinates must be positive"
        assert x2 <= 640 and y2 <= 480, f"Shelf {shelf_id} must fit standard 640x480 frame"


def test_shelf_rois_do_not_cross_exit_line():
    for shelf_id, (_, _, _, y2) in SHELF_ROIS.items():
        assert y2 < EXIT_LINE_Y, f"Shelf {shelf_id} bottom ({y2}) must be above exit line ({EXIT_LINE_Y})"


def test_exit_line_within_frame():
    assert 0 < EXIT_LINE_Y < 480