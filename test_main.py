from unittest.mock import patch, MagicMock
import numpy as np
import pytest

from cart_engine import VirtualCartEngine
from main import (
    detect_hand_points,
    evaluate_shelf_interaction,
    evaluate_exit,
    run_camera,
)
from store_config import SHELF_ROIS, PRODUCTS, EXIT_LINE_Y


# TC006 - Invalid Camera Access Handling
@patch('cv2.VideoCapture')
def test_run_camera_invalid_access(mock_video_capture):
    mock_instance = MagicMock()
    mock_instance.isOpened.return_value = False
    mock_video_capture.return_value = mock_instance

    with patch('builtins.print') as mock_print:
        result = run_camera(video_source=0, headless=True)
        assert result is None
        mock_print.assert_any_call("Failed to access camera.")


# TC007 - Detect Hand Motion Below the Threshold
def test_detect_hand_motion_below_threshold():
    # Synthetic mask with small noise contour (area < 1200)
    mask = np.zeros((480, 640), dtype=np.uint8)
    mask[50:60, 50:60] = 255  # 10x10 square = 100 area

    hand_points = detect_hand_points(mask, min_contour_area=1200)
    assert hand_points == []


def test_detect_hand_motion_above_threshold():
    # Synthetic mask with valid hand contour (area > 1200)
    mask = np.zeros((480, 640), dtype=np.uint8)
    mask[50:100, 50:100] = 255  # 50x50 square = 2500 area

    hand_points = detect_hand_points(mask, min_contour_area=1200)
    assert len(hand_points) == 1
    # Topmost y coordinate should be 50
    assert hand_points[0][1] == 50


# TC008 - Shelf Interaction and Cooldown
def test_shelf_interaction_pick_and_cooldown():
    cart_engine = VirtualCartEngine()
    cooldowns = {}
    shopper_id = 1

    # Coordinate inside shelf_soda ROI (20, 20, 150, 160)
    hx, hy = 50, 50
    interaction = evaluate_shelf_interaction(
        hx, hy, shopper_id, cart_engine, cooldowns
    )

    assert interaction == ("shelf_soda", PRODUCTS["shelf_soda"])
    assert cart_engine.carts[shopper_id]["items"][PRODUCTS["shelf_soda"]] == 1
    assert cooldowns.get(f"{shopper_id}_shelf_soda") == 40

    # Attempt second pick immediately while cooldown > 0
    second_pick = evaluate_shelf_interaction(
        hx, hy, shopper_id, cart_engine, cooldowns
    )
    assert second_pick is None
    # Cart count should still be 1
    assert cart_engine.carts[shopper_id]["items"][PRODUCTS["shelf_soda"]] == 1


def test_evaluate_exit_checkout():
    cart_engine = VirtualCartEngine()
    shopper_id = 1
    cart_engine.add_item(shopper_id, PRODUCTS["shelf_soda"])
    cooldowns = {}

    # Coordinate below exit line
    hy = EXIT_LINE_Y + 10
    receipt = evaluate_exit(hy, shopper_id, cart_engine, cooldowns)

    assert receipt is not None
    assert receipt[PRODUCTS["shelf_soda"]] == 1


def test_evaluate_exit_above_line():
    cart_engine = VirtualCartEngine()
    shopper_id = 1
    cart_engine.add_item(shopper_id, PRODUCTS["shelf_soda"])
    cooldowns = {}

    # Coordinate above exit line
    hy = EXIT_LINE_Y - 10
    receipt = evaluate_exit(hy, shopper_id, cart_engine, cooldowns)
    assert receipt is None


@patch('cv2.VideoCapture')
def test_run_camera_headless_loop(mock_video_capture):
    mock_instance = MagicMock()
    mock_instance.isOpened.return_value = True
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    mock_instance.read.return_value = (True, dummy_frame)
    mock_video_capture.return_value = mock_instance

    cart_engine = VirtualCartEngine()
    result = run_camera(
        video_source=0,
        headless=True,
        max_frames=3,
        cart_engine=cart_engine
    )

    assert result is not None
    assert mock_instance.read.call_count == 3