import argparse
import cv2
import numpy as np

from store_config import SHELF_ROIS, PRODUCTS, EXIT_LINE_Y
from cart_engine import VirtualCartEngine


def detect_hand_points(fg_mask, min_contour_area=1200):
    """
    Detect topmost contour points representing shopper hands from a foreground mask.
    """
    contours, _ = cv2.findContours(
        fg_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    valid_hand_points = []
    for cnt in contours:
        if cv2.contourArea(cnt) > min_contour_area:
            topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
            valid_hand_points.append(topmost)

    if valid_hand_points:
        valid_hand_points.sort(key=lambda pt: pt[1])

    return valid_hand_points


def process_frame(frame, bg_subtractor, min_contour_area=1200):
    """
    Applies background subtraction, cleans mask with morphology, and extracts hand coordinates.
    """
    fg_mask = bg_subtractor.apply(frame)

    kernel = np.ones((5, 5), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)

    hand_points = detect_hand_points(fg_mask, min_contour_area=min_contour_area)
    return fg_mask, hand_points


def evaluate_shelf_interaction(hx, hy, shopper_id, cart_engine, cooldowns, shelf_rois=SHELF_ROIS, products=PRODUCTS, cooldown_duration=40):
    """
    Checks if a hand coordinate (hx, hy) falls within any shelf ROI and adds item to cart.
    """
    for shelf_id, (sx1, sy1, sx2, sy2) in shelf_rois.items():
        if sx1 < hx < sx2 and sy1 < hy < sy2:
            cooldown_key = f"{shopper_id}_{shelf_id}"
            if cooldowns.get(cooldown_key, 0) <= 0:
                item_name = products[shelf_id]
                cart_engine.add_item(shopper_id, item_name)
                print(f"[+] HAND PICK DETECTED: {item_name}")
                cooldowns[cooldown_key] = cooldown_duration
                return shelf_id, item_name
    return None


def evaluate_exit(hy, shopper_id, cart_engine, cooldowns, exit_line_y=EXIT_LINE_Y):
    """
    Checks if a hand passes the checkout/exit threshold line and triggers receipt generation.
    """
    if hy > exit_line_y:
        checkout_cooldown_key = f"{shopper_id}_exit"
        if cooldowns.get(checkout_cooldown_key, 0) <= 0:
            receipt = cart_engine.generate_receipt(shopper_id)
            if receipt is not None:
                print("Customer exited. Camera shutting down...")
                return receipt
    return None


def draw_overlay(frame, hand_point, shelf_rois=SHELF_ROIS, products=PRODUCTS, exit_line_y=EXIT_LINE_Y):
    """
    Draws shelf bounding boxes, product labels, exit line, and hand tracker overlay onto frame.
    """
    h, w, _ = frame.shape

    # Draw shelves
    for shelf_id, (x1, y1, x2, y2) in shelf_rois.items():
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 165, 0), 2)
        cv2.putText(
            frame,
            products.get(shelf_id, shelf_id),
            (x1, y1 - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 165, 0),
            1
        )

    # Draw exit line
    cv2.line(frame, (0, exit_line_y), (w, exit_line_y), (0, 0, 255), 2)
    cv2.putText(
        frame,
        "SWIPE HAND HERE TO CHECKOUT",
        (10, exit_line_y - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        2
    )

    # Draw active hand if present
    if hand_point:
        hx, hy = hand_point
        cv2.circle(frame, (hx, hy), 10, (0, 255, 255), -1)
        cv2.putText(
            frame,
            "Active Hand",
            (hx + 15, hy),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1
        )

    return frame


def run_camera(video_source=0, headless=False, max_frames=None, cart_engine=None):
    """
    Main loop to run retail vision tracking on a camera feed, video file, or RTSP stream.
    """
    if cart_engine is None:
        cart_engine = VirtualCartEngine()

    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=300,
        varThreshold=50,
        detectShadows=False
    )

    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Failed to access camera.")
        return None

    cooldowns = {}
    single_shopper_id = 1
    frames_processed = 0

    print("Starting Motion-Based Hand Tracking... Press 'q' to quit.")

    try:
        while cap.isOpened():
            if max_frames is not None and frames_processed >= max_frames:
                break

            success, frame = cap.read()
            if not success or frame is None:
                print("Failed to access camera.")
                break

            frames_processed += 1
            frame = cv2.flip(frame, 1)

            # Process background subtraction & hand tracking
            _, hand_points = process_frame(frame, bg_subtractor)

            active_hand = None
            if hand_points:
                active_hand = hand_points[0]
                hx, hy = active_hand

                # A. Check shelf interaction
                evaluate_shelf_interaction(
                    hx, hy, single_shopper_id, cart_engine, cooldowns
                )

                # B. Check exit line
                receipt = evaluate_exit(
                    hy, single_shopper_id, cart_engine, cooldowns
                )
                if receipt is not None:
                    break

            # Decrease cooldown timers
            for key in list(cooldowns.keys()):
                if cooldowns[key] > 0:
                    cooldowns[key] -= 1

            # Render overlay if display enabled
            if not headless:
                draw_overlay(frame, active_hand)
                cv2.imshow("Amazon Go Simulation", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        cap.release()
        if not headless:
            try:
                cv2.destroyAllWindows()
            except (cv2.error, Exception):
                pass

    return cart_engine


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Amazon Go Simulation - Edge Vision Pipeline")
    parser.add_argument("--source", default=0, help="Video source (camera index, video file, or RTSP stream)")
    parser.add_argument("--headless", action="store_true", help="Run without UI window (for edge/Docker deployment)")
    args = parser.parse_args()

    src = int(args.source) if str(args.source).isdigit() else args.source
    run_camera(video_source=src, headless=args.headless)