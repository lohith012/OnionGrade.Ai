"""
Merges both Roboflow multiclass dataset and the Bulb Healthy/Unhealthy dataset
into a single unified classification dataset for YOLO training.

Dataset 1 (Roboflow): dataset/ with _classes.csv  -> good, damaged, rotten, sprouted
Dataset 2 (Bulb):     dataset_bulb_raw/New Onion - Copy/2. Bulb/
                        1. Healthy/ -> good
                        2. Unhealthy/ -> damaged

Output: dataset_merged/ with train/ and val/ sub-folders per class
"""

import os
import shutil
import random
import hashlib

random.seed(42)

MERGED_DIR = "dataset_merged"

# Classes for the merged dataset
CLASSES = ["good", "damaged", "rotten", "sprouted"]

# Max images to sample per class from the large bulb dataset (to keep training fast)
MAX_BULB_PER_CLASS = 500

def ensure_dirs():
    for split in ["train", "val"]:
        for cls in CLASSES:
            os.makedirs(os.path.join(MERGED_DIR, split, cls), exist_ok=True)

def copy_file_unique(src, dst_dir, prefix=""):
    """Copy file with a unique name to prevent collisions."""
    ext = os.path.splitext(src)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
        return False
    # Create unique name from path hash
    h = hashlib.md5(src.encode()).hexdigest()[:8]
    basename = os.path.basename(src)
    unique_name = f"{prefix}{h}_{basename}"
    dst = os.path.join(dst_dir, unique_name)
    try:
        shutil.copyfile(src, dst)
        return True
    except Exception as e:
        print(f"  Skip {src}: {e}")
        return False

def merge_roboflow_dataset():
    """Copy existing organized classification dataset (dataset_cls/)."""
    src_base = "dataset_cls"
    count = 0
    for split in ["train", "val"]:
        for cls in CLASSES:
            src_dir = os.path.join(src_base, split, cls)
            if not os.path.isdir(src_dir):
                continue
            dst_dir = os.path.join(MERGED_DIR, split, cls)
            for fname in os.listdir(src_dir):
                src_path = os.path.join(src_dir, fname)
                if os.path.isfile(src_path):
                    if copy_file_unique(src_path, dst_dir, prefix="rf_"):
                        count += 1
    print(f"[1] Roboflow dataset: copied {count} images")

def merge_bulb_dataset():
    """
    Copy bulb dataset images:
      Healthy (Red+White, Single+Multiple) -> good
      Unhealthy (Red+White, Single+Multiple) -> damaged
    
    We sample up to MAX_BULB_PER_CLASS to keep training feasible on CPU.
    Split 80/20 train/val.
    """
    bulb_base = os.path.join("dataset_bulb_raw", "New Onion - Copy", "2. Bulb")
    
    mapping = {
        "good": os.path.join(bulb_base, "1. Healthy"),
        "damaged": os.path.join(bulb_base, "2. Unhealthy"),
    }
    
    total = 0
    for cls_name, cls_dir in mapping.items():
        if not os.path.isdir(cls_dir):
            print(f"  Warning: {cls_dir} not found, skipping")
            continue
        
        # Collect all image files recursively
        all_images = []
        for root, dirs, files in os.walk(cls_dir):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
                    all_images.append(os.path.join(root, f))
        
        print(f"  Bulb '{cls_name}': found {len(all_images)} total images")
        
        # Sample to keep training fast
        if len(all_images) > MAX_BULB_PER_CLASS:
            random.shuffle(all_images)
            all_images = all_images[:MAX_BULB_PER_CLASS]
            print(f"    Sampled down to {len(all_images)} images")
        
        # Split 80/20
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
    
    print(f"[2] Bulb dataset: copied {total} images")

def print_summary():
    print("\n=== MERGED DATASET SUMMARY ===")
    for split in ["train", "val"]:
        print(f"\n  {split.upper()}:")
        for cls in CLASSES:
            d = os.path.join(MERGED_DIR, split, cls)
            count = len(os.listdir(d)) if os.path.isdir(d) else 0
            print(f"    {cls:>12}: {count} images")

if __name__ == "__main__":
    ensure_dirs()
    merge_roboflow_dataset()
    merge_bulb_dataset()
    print_summary()
    print("\nDone! Merged dataset ready at:", MERGED_DIR)
