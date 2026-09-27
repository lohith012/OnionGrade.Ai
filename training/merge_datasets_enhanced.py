"""
Enhanced Dataset Builder with Data Augmentation & Class Balancing.
Scales up the dataset to 3,000+ high-quality images with full augmentation
for maximum YOLO classification accuracy.
"""

import os
import shutil
import random
import hashlib
import cv2
import numpy as np

random.seed(42)

MERGED_DIR = "dataset_merged_v2"
CLASSES = ["good", "damaged", "rotten", "sprouted"]
MAX_BULB_PER_CLASS = 1000

def ensure_dirs():
    if os.path.exists(MERGED_DIR):
        shutil.rmtree(MERGED_DIR, ignore_errors=True)
    for split in ["train", "val"]:
        for cls in CLASSES:
            os.makedirs(os.path.join(MERGED_DIR, split, cls), exist_ok=True)

def copy_file_unique(src, dst_dir, prefix=""):
    ext = os.path.splitext(src)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
        return False
    h = hashlib.md5(src.encode()).hexdigest()[:8]
    basename = os.path.basename(src)
    unique_name = f"{prefix}{h}_{basename}"
    dst = os.path.join(dst_dir, unique_name)
    try:
        shutil.copyfile(src, dst)
        return True
    except Exception as e:
        return False

def augment_image(img):
    """Applies random realistic agricultural augmentations."""
    h, w = img.shape[:2]
    aug_list = []
    
    # 1. Horizontal Flip
    aug_list.append(cv2.flip(img, 1))
    
    # 2. Random 90 deg rotation
    aug_list.append(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))
    
    # 3. Brightness / Contrast jitter
    alpha = random.uniform(0.85, 1.15)
    beta = random.randint(-15, 15)
    jittered = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    aug_list.append(jittered)
    
    # 4. Slight Gaussian Blur
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    aug_list.append(blurred)
    
    return aug_list

def merge_roboflow_dataset_with_augmentation():
    """Copy Roboflow dataset and augment minority classes (rotten, sprouted)."""
    src_base = "dataset_cls"
    count = 0
    aug_count = 0
    
    for split in ["train", "val"]:
        for cls in CLASSES:
            src_dir = os.path.join(src_base, split, cls)
            if not os.path.isdir(src_dir):
                continue
            dst_dir = os.path.join(MERGED_DIR, split, cls)
            
            for fname in os.listdir(src_dir):
                src_path = os.path.join(src_dir, fname)
                if not os.path.isfile(src_path):
                    continue
                if copy_file_unique(src_path, dst_dir, prefix="rf_"):
                    count += 1
                
                # If training split and minority class, apply augmentations
                if split == "train" and cls in ("rotten", "sprouted", "damaged"):
                    img = cv2.imread(src_path)
                    if img is not None:
                        augs = augment_image(img)
                        for idx, a_img in enumerate(augs):
                            aug_name = f"aug_{cls}_{idx}_{fname}"
                            cv2.imwrite(os.path.join(dst_dir, aug_name), a_img)
                            aug_count += 1

    print(f"[1] Roboflow + Augmented: {count} original + {aug_count} augmented images")

def merge_bulb_dataset():
    """Sample up to MAX_BULB_PER_CLASS images from 12,000+ bulb dataset."""
    bulb_base = os.path.join("dataset_bulb_raw", "New Onion - Copy", "2. Bulb")
    mapping = {
        "good": os.path.join(bulb_base, "1. Healthy"),
        "damaged": os.path.join(bulb_base, "2. Unhealthy"),
    }
    
    total = 0
    for cls_name, cls_dir in mapping.items():
        if not os.path.isdir(cls_dir):
            continue
        all_images = []
        for root, _, files in os.walk(cls_dir):
            for f in files:
                if os.path.splitext(f)[1].lower() in (".jpg", ".jpeg", ".png", ".webp"):
                    all_images.append(os.path.join(root, f))
        
        if len(all_images) > MAX_BULB_PER_CLASS:
            random.shuffle(all_images)
            all_images = all_images[:MAX_BULB_PER_CLASS]
            
        random.shuffle(all_images)
        split_idx = int(len(all_images) * 0.8)
        train_imgs = all_images[:split_idx]
        val_imgs = all_images[split_idx:]
        
        for img_path in train_imgs:
            if copy_file_unique(img_path, os.path.join(MERGED_DIR, "train", cls_name), prefix="bulb_"):
                total += 1
        for img_path in val_imgs:
            if copy_file_unique(img_path, os.path.join(MERGED_DIR, "val", cls_name), prefix="bulb_"):
                total += 1
                
    print(f"[2] Bulb dataset: added {total} real images")

def print_summary():
    print("\n=== ENHANCED DATASET SUMMARY ===")
    total_imgs = 0
    for split in ["train", "val"]:
        print(f"\n  {split.upper()}:")
        for cls in CLASSES:
            d = os.path.join(MERGED_DIR, split, cls)
            count = len(os.listdir(d)) if os.path.isdir(d) else 0
            total_imgs += count
            print(f"    {cls:>12}: {count} images")
    print(f"\nTotal Dataset Size: {total_imgs} images")

if __name__ == "__main__":
    ensure_dirs()
    merge_roboflow_dataset_with_augmentation()
    merge_bulb_dataset()
    print_summary()
