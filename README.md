# Autonomous Retail Checkout Simulation (Amazon Go / "Just Walk Out")

An edge-deployable computer vision pipeline and virtual shopping cart engine for autonomous retail environments. The system uses computer vision to track shopper hand interactions across designated shelf regions, automatically updates a virtual cart, and calculates itemized receipts upon crossing a checkout boundary.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph Edge Vision Pipeline
        A["Camera Input\n(Webcam, Video File, or RTSP)"] --> B["Background Subtraction\n(MOG2 + Morphology)"]
        B --> C["Contour Detection &\nTopmost Hand Extraction"]
    end

    subgraph Interaction & Cart Engine
        C --> D{"Hand in Shelf ROI?"}
        D -- Yes --> E["Add Item to Cart &\nTrigger Cooldown"]
        D -- No --> F{"Hand crosses Exit Line?"}
        F -- Yes --> G["Generate Receipt &\nFinalize Session"]
        E --> H["Virtual Cart Engine\n(In-memory Cart State)"]
        H --> G
    end
```

---

## Project Structure

```
.
├── main.py                 # Core vision processing loop, interaction handlers & CLI
├── cart_engine.py          # Virtual cart engine & receipt generation
├── store_config.py         # Shelf ROI boundaries, product catalog & exit line
├── yolov8n.pt              # YOLOv8 nano model for deep learning object detection
├── requirements.txt        # Python dependency manifest
├── Dockerfile              # Production-ready headless edge container image
├── test_cart_engine.py     # Unit tests for cart state management
├── test_main.py            # Unit and integration tests for CV & interaction logic
├── test_store_config.py    # Geometry & catalog invariant tests
├── TEST_PLAN.md            # Test specification and coverage document
└── TEST_FAILURE_REPORT.md  # Test execution & resolution report
```

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Application

### 1. Interactive Desktop Mode (Webcam with GUI)
Runs the live webcam feed with bounding box and hand-tracking overlays:
```bash
python main.py
```
- Hover your hand into a shelf box at the top to pick an item.
- Swipe your hand across the red line at the bottom to check out.
- Press `q` to quit manually.

### 2. Edge / Headless Mode
Ideal for running on edge gateways, headless Linux servers, or Docker containers without an active display:
```bash
python main.py --headless
```

### 3. Custom Video Source or RTSP Stream (Forward Deployed Edge Mode)
Ingest from a pre-recorded test video or an IP camera RTSP feed:
```bash
# Video file
python main.py --source demo_shelf_walkthrough.mp4

# RTSP Stream from an aisle camera
python main.py --source rtsp://admin:password@192.168.1.100:554/h264Preview_01_main --headless
```

---

## Docker Deployment

Build and run the containerized edge appliance:

```bash
# Build Docker image
docker build -t retail-edge-vision:latest .

# Run container (headless mode)
docker run --rm -it retail-edge-vision:latest
```

---

## Running Tests

Execute the comprehensive test suite with `pytest`:

```bash
pytest -v
```

All 17 tests validate:
- Cart initialization, item addition, and receipt formatting
- Cooldown timers preventing duplicate item registrations
- Contour noise filtering (ignoring movements below threshold)
- Frame boundary and shelf ROI geometry invariants
- Headless camera execution and graceful camera access error handling

---

## Forward Deployed Engineering (FDE) Features

- **Decoupled Architecture**: Vision processing is separated into pure functions (`process_frame`, `evaluate_shelf_interaction`, `evaluate_exit`) enabling standalone testing and distributed event streaming.
- **Headless Resiliency**: Safe handling of headless environments avoids OpenCV GUI runtime crashes on Linux servers and Docker containers.
- **Flexible Stream Ingestion**: First-class support for RTSP streams, local video files, and camera indices.
- **Store Configuration Extensibility**: [store_config.py](file:///d:/Amazon/store_config.py) isolates store geometry from business logic, paving the way for multi-camera calibration and dynamic store layout onboarding.