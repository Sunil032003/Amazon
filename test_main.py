import pytest
from unittest.mock import patch, MagicMock
from main import run_camera
from cart_engine import VirtualCartEngine
from store_config import SHELF_ROIS, PRODUCTS, EXIT_LINE_Y

# TC006 - Invalid Camera Access Handling
@patch('cv2.VideoCapture')
def test_run_camera_invalid_access(mock_video_capture):
    mock_video_capture.return_value.isOpened.return_value = False
    with patch('builtins.print') as mock_print:
        run_camera()
        mock_print.assert_called_with("Failed to access camera.")

# TC007 - Detect Hand Motion Below the Threshold
@patch('cv2.VideoCapture')
@patch('cv2.findContours')
def test_run_camera_small_hand_movement(mock_find_contours, mock_video_capture):
    mock_video_capture.return_value.isOpened.return_value = True
    mock_video_capture.return_value.read.return_value = (True, MagicMock(shape=(720, 1280, 3)))
    mock_find_contours.return_value = ([], None)

    with patch('builtins.print') as mock_print:
        run_camera()
        mock_print.assert_called_with("Starting Motion-Based Hand Tracking... Press 'q' to quit.")

# TC008 - Shelf Interaction Timeout
@patch('cv2.VideoCapture')
@patch('cart_engine.VirtualCartEngine.add_item')
@patch('cv2.findContours')
def test_run_camera_shelf_interaction_timeout(mock_find_contours, mock_add_item, mock_video_capture):
    mock_video_capture.return_value.isOpened.return_value = True
    mock_video_capture.return_value.read.return_value = (True, MagicMock(shape=(720, 1280, 3)))

    # Create a valid contour that exceeds the area threshold
    valid_contour = MagicMock()
    valid_contour.side_effect = [MagicMock(shape=(5, 1, 2)), MagicMock(shape=(5, 1, 2))]
    mock_find_contours.return_value = ([valid_contour], None)

    mock_add_item.return_value = None
    
    # Simulate cooldown passing
    for _ in range(40):  # Ensure we are beyond the cooldown period
        run_camera()

    # Ensure add_item is called only once per interaction
    assert mock_add_item.call_count == 1