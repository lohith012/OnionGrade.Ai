# Models Directory

Place your trained Ultralytics YOLO model weight file here:

```text
models/
└── best.pt
```

### Modes:
- If `best.pt` is missing or `AI_MODE=demo` in `.env`, the system automatically runs the high-fidelity demo inference engine with realistic OpenCV object detection.
- Once you drop `best.pt` here and set `AI_MODE=real`, the live YOLO object detector is activated automatically upon restart.
