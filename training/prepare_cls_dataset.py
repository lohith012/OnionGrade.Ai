import os
import csv
import shutil

def prepare_classification_dataset():
    base_src = "dataset"
    base_dst = "dataset_cls"
    
    splits = {
        "train": "train",
        "valid": "val"
    }
    
    classes = ["good", "damaged", "rotten", "sprouted"]
    
    for split_src, split_dst in splits.items():
        csv_file = os.path.join(base_src, split_src, "_classes.csv")
        if not os.path.exists(csv_file):
            print(f"Skipping {split_src}, {csv_file} does not exist.")
            continue
            
        with open(csv_file, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            # Find column indices
            col_map = {col.strip(): idx for idx, col in enumerate(header)}
            
            for row in reader:
                fname = row[0].strip()
                is_damaged = row[col_map["Damaged"]].strip() == "1" if "Damaged" in col_map else False
                is_healthy = row[col_map["Healthy"]].strip() == "1" if "Healthy" in col_map else False
                is_rotten = row[col_map["Rotten"]].strip() == "1" if "Rotten" in col_map else False
                is_sprouted = row[col_map["Sprouted"]].strip() == "1" if "Sprouted" in col_map else False
                
                # Priority: Rotten > Sprouted > Damaged > Good
                if is_rotten:
                    cls_name = "rotten"
                elif is_sprouted:
                    cls_name = "sprouted"
                elif is_damaged:
                    cls_name = "damaged"
                elif is_healthy:
                    cls_name = "good"
                else:
                    cls_name = "good"
                    
                src_img = os.path.join(base_src, split_src, fname)
                if not os.path.exists(src_img):
                    continue
                    
                dst_dir = os.path.join(base_dst, split_dst, cls_name)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copyfile(src_img, os.path.join(dst_dir, fname))

    print("Classification dataset organized in dataset_cls/!")

if __name__ == "__main__":
    prepare_classification_dataset()
