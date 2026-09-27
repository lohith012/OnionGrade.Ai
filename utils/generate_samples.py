import os
import math
import random
import cv2
import numpy as np

def generate_sample_images(output_dir="static/demo"):
    os.makedirs(output_dir, exist_ok=True)
    
    samples = [
        {"name": "sample_onions_batch.jpg", "count": 14, "defects": ["damaged", "rotten", "sprouted"]},
        {"name": "sample_mixed_onions.jpg", "count": 18, "defects": ["good", "damaged", "undersized"]},
        {"name": "sample_harvest_onions.jpg", "count": 12, "defects": ["good", "sprouted", "rotten", "undersized"]}
    ]
    
    for sample in samples:
        w, h = 960, 720
        # Background: rustic agricultural wooden/jute texture
        bg = np.full((h, w, 3), (215, 225, 230), dtype=np.uint8)
        
        # Add subtle noise/texture to background
        noise = np.random.normal(0, 8, (h, w, 3)).astype(np.int16)
        bg = np.clip(bg.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        rng = random.Random(hash(sample["name"]))
        
        # Draw onion bulbs
        cols = 5
        rows = math.ceil(sample["count"] / cols)
        
        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= sample["count"]:
                    break
                
                cx = int(120 + c * (w - 240) / (cols - 1) + rng.randint(-25, 25))
                cy = int(120 + r * (h - 240) / max(1, rows - 1) + rng.randint(-25, 25))
                radius = rng.randint(45, 68)
                
                # Assign defect type
                defect_type = rng.choice(sample["defects"] + ["good", "good", "good"])
                
                # Base onion color (red/pink onion tones)
                # Outer skins: brownish purple / golden red
                base_color = (rng.randint(60, 90), rng.randint(50, 80), rng.randint(140, 180)) # BGR
                
                # Onion shadow
                cv2.ellipse(bg, (cx + 8, cy + 12), (radius + 6, radius - 4), 15, 0, 360, (160, 175, 185), -1)
                
                # Onion bulb
                cv2.circle(bg, (cx, cy), radius, base_color, -1)
                
                # Concentric onion skin layers & highlights
                for dr in range(radius - 5, 10, -8):
                    layer_color = (
                        min(255, base_color[0] + rng.randint(5, 20)),
                        min(255, base_color[1] + rng.randint(5, 20)),
                        min(255, base_color[2] + rng.randint(5, 25))
                    )
                    cv2.ellipse(bg, (cx - 3, cy - 3), (dr, int(dr * 0.9)), rng.randint(-10, 10), 0, 360, layer_color, 2)
                    
                # Defect visual characteristics
                if defect_type == "rotten":
                    # Dark black/brown mold patch
                    rx = cx + rng.randint(-15, 15)
                    ry = cy + rng.randint(-15, 15)
                    cv2.circle(bg, (rx, ry), rng.randint(18, 28), (25, 30, 40), -1)
                    cv2.circle(bg, (rx, ry), rng.randint(10, 16), (40, 50, 70), -1)
                elif defect_type == "damaged":
                    # Bruised/cut slice
                    cv2.ellipse(bg, (cx + 10, cy - 10), (22, 12), 45, 0, 360, (40, 110, 180), -1)
                elif defect_type == "sprouted":
                    # Green sprout shooting out top
                    sprout_pts = np.array([
                        [cx - 5, cy - radius + 5],
                        [cx - 15, cy - radius - 35],
                        [cx + 8, cy - radius - 30],
                        [cx + 5, cy - radius + 5]
                    ], np.int32)
                    cv2.fillPoly(bg, [sprout_pts], (40, 160, 50))
                    cv2.polylines(bg, [sprout_pts], True, (20, 120, 30), 2)
                elif defect_type == "undersized":
                    # Draw a noticeably smaller onion
                    pass
                    
                # Onion neck and root tip
                cv2.circle(bg, (cx, cy - radius + 2), 7, (40, 60, 100), -1)
                cv2.circle(bg, (cx, cy + radius - 2), 6, (80, 110, 130), -1)
                
                idx += 1
                
        out_file = os.path.join(output_dir, sample["name"])
        cv2.imwrite(out_file, bg)
        print(f"Generated sample image: {out_file}")

if __name__ == "__main__":
    generate_sample_images()
