# OnionVision AI – Model Training Guide

This guide describes how to train a custom Ultralytics YOLO object detection model on onion quality datasets and deploy it into OnionVision AI.

---

## 1. Quality Defect Classes

Label your dataset with the following 5 standardized classes:

| Class ID | Name | Description |
|---|---|---|
| `0` | **good** | Sound, firm onion bulb with intact dry wrapper skin |
| `1` | **damaged** | Mechanical cuts, bruises, gouges, peeled outer scales |
| `2` | **rotten** | Black/blue mold (*Aspergillus niger*), bacterial soft rot |
| `3` | **sprouted** | Green emergent vegetative shoots |
| `4` | **undersized** | Bulb caliber &lt; 40 mm |

---

## 2. Dataset Directory Structure

Organize your annotated dataset into YOLO standard format:

```text
dataset/
├── data.yaml
├── images/
│   ├── train/
│   │   ├── img_001.jpg
│   │   └── img_002.jpg
│   └── val/
│       ├── img_101.jpg
│       └── img_102.jpg
└── labels/
    ├── train/
    │   ├── img_001.txt
    │   └── img_002.txt
    └── val/
        ├── img_101.txt
        └── img_102.txt
```

Each label `.txt` file contains bounding boxes in normalized coordinates:
`<class_id> <x_center> <y_center> <width> <height>`

---

## 3. Training Command

Run the training pipeline with Ultralytics YOLO:

```bash
# Activate your virtual environment
.\venv\Scripts\activate

# Train YOLOv11 nano or small model on your dataset
yolo detect train data=training/data.yaml model=yolo11n.pt epochs=50 imgsz=640 batch=16 plots=True
```

For GPU acceleration (NVIDIA CUDA):
```bash
yolo detect train data=training/data.yaml model=yolo11n.pt epochs=50 imgsz=640 device=0
```

---

## 4. Validating Model Performance

After training finishes, review confusion matrices, mAP@50, and precision-recall curves:

```bash
yolo detect val model=runs/detect/train/weights/best.pt data=training/data.yaml
```

---

## 5. Deploying the Model into OnionVision AI

1. Copy the resulting weight file:
   ```bash
   cp runs/detect/train/weights/best.pt models/best.pt
   ```
2. Enable real inference in `.env`:
   ```env
   AI_MODE=real
   MODEL_PATH=models/best.pt
   ```
3. Restart the web server:
   ```bash
   python app.py
   ```
4. The application will detect `models/best.pt` and use real YOLO inference for all future inspections!
