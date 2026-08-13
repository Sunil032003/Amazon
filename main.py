import cv2
import numpy as np

from store_config import SHELF_ROIS, PRODUCTS, EXIT_LINE_Y
from cart_engine import VirtualCartEngine


def run_camera():

    # Initialize Cart Engine
    cart_engine = VirtualCartEngine()

    # Background Subtractor
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=300,
        varThreshold=50,
        detectShadows=False
    )

    cap = cv2.VideoCapture(0)

    cooldowns = {}

    SINGLE_SHOPPER_ID = 1

    print("Starting Motion-Based Hand Tracking... Press 'q' to quit.")

    while cap.isOpened():

        success, frame = cap.read()

        if not success:
            print("Failed to access camera.")
            break

        # Mirror the frame
        frame = cv2.flip(frame, 1)

        h, w, _ = frame.shape

        # 1. Background subtraction
        fg_mask = bg_subtractor.apply(frame)

        # Clean mask
        kernel = np.ones((5, 5), np.uint8)

        fg_mask = cv2.morphologyEx(
            fg_mask,
            cv2.MORPH_OPEN,
            kernel
        )

        fg_mask = cv2.dilate(
            fg_mask,
            kernel,
            iterations=2
        )

        # 2. Find contours
        contours, _ = cv2.findContours(
            fg_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        valid_hand_points = []

        for cnt in contours:

            # Ignore small movements
            if cv2.contourArea(cnt) > 1200:

                # Find topmost point
                topmost = tuple(
                    cnt[cnt[:, :, 1].argmin()][0]
                )

                valid_hand_points.append(topmost)

        # If hand detected
        if valid_hand_points:

            # Get highest point
            valid_hand_points.sort(
                key=lambda pt: pt[1]
            )

            hx, hy = valid_hand_points[0]

            # Draw hand point
            cv2.circle(
                frame,
                (hx, hy),
                10,
                (0, 255, 255),
                -1
            )

            cv2.putText(
                frame,
                "Active Hand",
                (hx + 15, hy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1
            )

            # A. Check shelf interaction
            for shelf_id, (
                sx1,
                sy1,
                sx2,
                sy2
            ) in SHELF_ROIS.items():

                if (
                    sx1 < hx < sx2
                    and sy1 < hy < sy2
                ):

                    cooldown_key = (
                        f"{SINGLE_SHOPPER_ID}_{shelf_id}"
                    )

                    if cooldowns.get(
                        cooldown_key,
                        0
                    ) <= 0:

                        cart_engine.add_item(
                            SINGLE_SHOPPER_ID,
                            PRODUCTS[shelf_id]
                        )

                        print(
                            f"[+] HAND PICK DETECTED: "
                            f"{PRODUCTS[shelf_id]}"
                        )

                        cooldowns[cooldown_key] = 40

            # B. Check exit line
            if hy > EXIT_LINE_Y:

                checkout_cooldown_key = (
                    f"{SINGLE_SHOPPER_ID}_exit"
                )

                if cooldowns.get(
                    checkout_cooldown_key,
                    0
                ) <= 0:

                    receipt = cart_engine.generate_receipt(
                        SINGLE_SHOPPER_ID
                    )

                    if receipt is not None:

                        print(
                            "Customer exited. "
                            "Camera shutting down..."
                        )

                        cap.release()
                        cv2.destroyAllWindows()

                        break

        # Decrease cooldown timers
        for key in list(cooldowns.keys()):

            if cooldowns[key] > 0:
                cooldowns[key] -= 1

        # Draw shelf boxes
        for shelf_id, (
            x1,
            y1,
            x2,
            y2
        ) in SHELF_ROIS.items():

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 165, 0),
                2
            )

            cv2.putText(
                frame,
                PRODUCTS[shelf_id],
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 165, 0),
                1
            )

        # Draw exit line
        cv2.line(
            frame,
            (0, EXIT_LINE_Y),
            (w, EXIT_LINE_Y),
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            "SWIPE HAND HERE TO CHECKOUT",
            (10, EXIT_LINE_Y - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2
        )

        # Show camera
        cv2.imshow(
            "Amazon Go Simulation",
            frame
        )

        # Press q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


# Only start camera when main.py is executed directly
if __name__ == "__main__":
    run_camera()