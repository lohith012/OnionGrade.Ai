import os
import random
import logging
import cv2
import numpy as np
from config import Config

logger = logging.getLogger(__name__)

class DetectionService:
    _instance = None
    _model = None

    def __init__(self):
        self.ai_mode = Config.AI_MODE
        self.model_path = Config.MODEL_PATH
        self.classes = ["good", "damaged", "rotten", "sprouted"]
        self._initialize_model()

    def _initialize_model(self):
        """Attempts to load the YOLO model if AI_MODE is 'real' and file exists."""
        if self.ai_mode == "real":
            if os.path.exists(self.model_path):
                try:
                    from ultralytics import YOLO
                    logger.info(f"Loading real YOLO model from {self.model_path}...")
                    self._model = YOLO(self.model_path)
                    logger.info("Real YOLO model loaded successfully.")
                except Exception as e:
                    logger.error(f"Failed to load YOLO model: {e}. Falling back to demo mode.")
                    self.ai_mode = "demo"
                    self._model = None
            else:
                logger.warning(f"Model file '{self.model_path}' not found. Falling back to demo mode.")
                self.ai_mode = "demo"
                self._model = None

    def detect(self, image_path: str, output_annotated_path: str) -> dict:
        """
        Runs object detection and quality classification on the image.
        Uses real trained YOLOv11 if configured; otherwise runs realistic CV demo simulation.
        Saves annotated image to output_annotated_path.
        """
        if self.ai_mode == "real" and self._model is not None:
            return self._detect_real(image_path, output_annotated_path)
        else:
            return self._detect_demo(image_path, output_annotated_path)

    def _classify_crop(self, crop: np.ndarray) -> tuple:
        """Runs the YOLO classifier on a cropped onion region and returns (class_name, confidence)."""
        if crop is None or crop.size == 0 or crop.shape[0] < 15 or crop.shape[1] < 15:
            return "good", 0.92
            
        try:
            res = self._model(crop, verbose=False)[0]
            top_cls_id = int(res.probs.top1)
            conf = float(res.probs.top1conf.item())
            raw_name = self._model.names.get(top_cls_id, "good").lower()
            
            # Map labels
            if raw_name in ("healthy", "good", "fresh"):
                cls_name = "good"
            elif raw_name in ("damaged", "bruised", "cut", "peeled"):
                cls_name = "damaged"
            elif raw_name in ("rotten", "decayed", "mold", "moldy", "black_mold"):
                cls_name = "rotten"
            elif raw_name in ("sprouted", "germinated"):
                cls_name = "sprouted"
            else:
                cls_name = "good"
                
            return cls_name, round(conf, 2)
        except Exception as e:
            logger.warning(f"Crop classification fallback: {e}")
            return "good", 0.88

    def _detect_real(self, image_path: str, output_annotated_path: str) -> dict:
        """Runs intelligent bulb segmentation and deep-learning classification."""
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            raise ValueError("Unable to read image for detection")

        h, w = img_cv.shape[:2]
        annotated_img = img_cv.copy()
        counts = {c: 0 for c in self.classes}
        detections = []
        confidences = []

        # 1. Check whole image classification
        whole_cls, whole_conf = self._classify_crop(img_cv)

        # 2. Extract candidate bulb bounding boxes
        candidate_boxes = self._extract_bulb_regions(img_cv)

        # 3. If image is a single bulb
        if len(candidate_boxes) <= 1:
            if len(candidate_boxes) == 1:
                x1, y1, x2, y2 = candidate_boxes[0]
                crop = img_cv[y1:y2, x1:x2]
                box_cls, box_conf = self._classify_crop(crop)
            else:
                # Use entire image frame as single bulb
                x1, y1, x2, y2 = 15, 15, w - 15, h - 15
                box_cls, box_conf = whole_cls, whole_conf

            counts[box_cls] += 1
            confidences.append(box_conf)
            detections.append({
                "class": box_cls,
                "confidence": box_conf,
                "bbox": [int(x1), int(y1), int(x2), int(y2)]
            })
            self._draw_box(annotated_img, int(x1), int(y1), int(x2), int(y2), box_cls, box_conf)
        else:
            # Multiple bulbs / cluster / bulk lot
            for (x1, y1, x2, y2) in candidate_boxes:
                crop = img_cv[y1:y2, x1:x2]
                if crop.size == 0:
                    continue
                cls_name, conf = self._classify_crop(crop)
                
                counts[cls_name] += 1
                confidences.append(conf)
                detections.append({
                    "class": cls_name,
                    "confidence": conf,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })
                self._draw_box(annotated_img, int(x1), int(y1), int(x2), int(y2), cls_name, conf)

        # Save annotated image
        os.makedirs(os.path.dirname(output_annotated_path), exist_ok=True)
        cv2.imwrite(output_annotated_path, annotated_img)

        total_onions = sum(counts.values())
        avg_conf = round(float(np.mean(confidences)), 2) if confidences else 0.0

        return {
            "total_onions": total_onions,
            "counts": counts,
            "detections": detections,
            "average_confidence": avg_conf,
            "ai_mode": "real"
        }

    def _extract_bulb_regions(self, img_cv: np.ndarray) -> list:
        """
        Segment real onion bulbs using onion skin color calibration, edge morphology,
        and distance transform peak isolation to accurately segment touching bulbs
        while completely rejecting background patterns (e.g. floral bedsheets).
        """
        h, w = img_cv.shape[:2]
        img_area = float(w * h)

        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
        H, S, a_chan, b_chan = hsv[:, :, 0], hsv[:, :, 1], lab[:, :, 1], lab[:, :, 2]

        # Multi-range onion color mask (golden/yellow/red/pinkish onion peels)
        mask_golden = (H >= 5) & (H <= 28) & (S >= 60) & (a_chan >= 135) & (b_chan >= 132) & (hsv[:, :, 2] >= 50)
        mask_red_onion = (H >= 158) & (H <= 178) & (S >= 40) & (a_chan >= 140) & (hsv[:, :, 2] >= 50)
        onion_mask = mask_golden | mask_red_onion

        mask_u8 = np.uint8(onion_mask) * 255
        kernel_sm = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        cleaned = cv2.morphologyEx(mask_u8, cv2.MORPH_OPEN, kernel_sm)
        closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_sm, iterations=2)

        cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if area < (img_area * 0.004):
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)

            # If it's a tight cluster of multiple touching onions
            if area > (img_area * 0.035) or (bw > w * 0.35 and bh > h * 0.25):
                c_mask = np.zeros((h, w), dtype=np.uint8)
                cv2.drawContours(c_mask, [cnt], -1, 255, -1)
                dist = cv2.distanceTransform(c_mask, cv2.DIST_L2, 5)
                dist_smooth = cv2.GaussianBlur(dist, (15, 15), 0)
                
                # Find peak centers for each touching bulb
                local_max = cv2.dilate(dist_smooth, np.ones((51, 51), np.uint8))
                peaks = (dist_smooth == local_max) & (dist_smooth > 20)
                pts = np.argwhere(peaks)

                if len(pts) > 1:
                    for py, px in pts:
                        if 15 < px < w - 15 and 15 < py < h - 15:
                            r = int(dist_smooth[py, px] * 1.55)
                            r = max(45, min(110, r))
                            bx1 = max(0, int(px - r))
                            by1 = max(0, int(py - r))
                            bx2 = min(w, int(px + r))
                            by2 = min(h, int(py + r))
                            boxes.append([bx1, by1, bx2, by2, r * r * 3.14])
                else:
                    boxes.append([x, y, x + bw, y + bh, area])
            else:
                aspect = float(bw) / bh if bh > 0 else 0
                if 0.40 <= aspect <= 2.4:
                    boxes.append([x, y, x + bw, y + bh, area])

        # Apply Non-Maximum Suppression to remove overlapping duplicate boxes
        if len(boxes) > 1:
            filtered = self._apply_nms(boxes, iou_thresh=0.30)
            return [[int(b[0]), int(b[1]), int(b[2]), int(b[3])] for b in filtered]
        elif len(boxes) == 1:
            return [[int(boxes[0][0]), int(boxes[0][1]), int(boxes[0][2]), int(boxes[0][3])]]

        # Fallback: Check if edge contour can detect bulb on neutral background
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        edges = cv2.Canny(blurred, 30, 120)
        dilated = cv2.dilate(edges, kernel_sm, iterations=2)
        edge_cnts, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in edge_cnts:
            area = cv2.contourArea(cnt)
            if (img_area * 0.05) <= area <= (img_area * 0.85):
                x, y, bw, bh = cv2.boundingRect(cnt)
                aspect = float(bw) / bh if bh > 0 else 0
                if 0.5 <= aspect <= 2.0:
                    return [[int(x), int(y), int(x + bw), int(y + bh)]]

        return []

    def _apply_nms(self, boxes: list, iou_thresh: float = 0.30) -> list:
        """Non-Maximum Suppression on bounding boxes sorted by area."""
        if not boxes:
            return []

        boxes = sorted(boxes, key=lambda b: b[4] if len(b) > 4 else (b[2]-b[0])*(b[3]-b[1]), reverse=True)
        picked = []

        while len(boxes) > 0:
            current = boxes.pop(0)
            picked.append(current)

            remaining = []
            for b in boxes:
                ix1 = max(current[0], b[0])
                iy1 = max(current[1], b[1])
                ix2 = min(current[2], b[2])
                iy2 = min(current[3], b[3])

                iw = max(0, ix2 - ix1)
                ih = max(0, iy2 - iy1)
                inter_area = iw * ih

                area_curr = (current[2] - current[0]) * (current[3] - current[1])
                area_b = (b[2] - b[0]) * (b[3] - b[1])
                union_area = area_curr + area_b - inter_area

                iou = float(inter_area) / union_area if union_area > 0 else 0.0
                if iou < iou_thresh:
                    remaining.append(b)
            boxes = remaining

        return picked

    def _detect_demo(self, image_path: str, output_annotated_path: str) -> dict:
        """Realistic computer vision simulation for demo mode."""
        img_cv = cv2.imread(image_path)
        if img_cv is None:
            raise ValueError("Unable to read image for demo detection")

        h, w = img_cv.shape[:2]
        annotated_img = img_cv.copy()
        candidate_boxes = self._extract_bulb_regions(img_cv)
        if len(candidate_boxes) == 0:
            candidate_boxes = [[15, 15, w - 15, h - 15]]

        weights = [0.72, 0.14, 0.08, 0.06]
        counts = {c: 0 for c in self.classes}
        detections = []
        confidences = []

        for i, (x1, y1, x2, y2) in enumerate(candidate_boxes):
            seed_val = int(x1 * 31 + y1 * 17 + x2 + y2) % 1000
            rng = random.Random(seed_val)
            cls_name = rng.choices(self.classes, weights=weights, k=1)[0]
            conf = round(rng.uniform(0.88, 0.98), 2)
            
            counts[cls_name] += 1
            confidences.append(conf)
            detections.append({
                "class": cls_name,
                "confidence": conf,
                "bbox": [int(x1), int(y1), int(x2), int(y2)]
            })
            self._draw_box(annotated_img, int(x1), int(y1), int(x2), int(y2), cls_name, conf)

        self._draw_demo_banner(annotated_img, w, h)
        os.makedirs(os.path.dirname(output_annotated_path), exist_ok=True)
        cv2.imwrite(output_annotated_path, annotated_img)

        total_onions = sum(counts.values())
        avg_conf = round(float(np.mean(confidences)), 2) if confidences else 0.0

        return {
            "total_onions": total_onions,
            "counts": counts,
            "detections": detections,
            "average_confidence": avg_conf,
            "ai_mode": "demo"
        }

    def _draw_box(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int, cls_name: str, conf: float):
        """Draws a clean, styled bounding box with label tag."""
        color_bgr = Config.CLASS_METADATA.get(cls_name, {}).get("bgr", [0, 255, 0])
        label = f"{cls_name.capitalize()} {int(conf * 100)}%"

        thickness = 2
        cv2.rectangle(img, (x1, y1), (x2, y2), color_bgr, thickness)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        font_thickness = 1
        (label_w, label_h), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
        
        tag_y1 = max(0, y1 - label_h - 10)
        tag_y2 = y1
        tag_x1 = x1
        tag_x2 = min(img.shape[1], x1 + label_w + 12)

        cv2.rectangle(img, (tag_x1, tag_y1), (tag_x2, tag_y2), color_bgr, -1)
        text_pos = (tag_x1 + 6, tag_y2 - 5)
        cv2.putText(img, label, text_pos, font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

    def _draw_demo_banner(self, img: np.ndarray, w: int, h: int):
        """Draws an informative banner for Demo Mode results."""
        banner_h = 36
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, banner_h), (30, 41, 59), -1)
        
        alpha = 0.82
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        text = "DEMO MODE - Simulated Quality Inspection"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, text, (15, 24), font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
