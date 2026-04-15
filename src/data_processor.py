"""
Data processing script to split raw images into train/val/test folders.
"""

import os
import shutil
from sklearn.model_selection import train_test_split
import random

# Set seed for reproducibility
random.seed(42)

# Paths
RAW_DIR = "data/raw/images"
PROCESSED_DIR = "data/processed"

def create_processed_structure():
    """Create the train/val/test folder structure"""
    for split in ['train', 'val', 'test']:
        for category in ['bread', 'champagnes', 'milk', 'sugar']:
            os.makedirs(os.path.join(PROCESSED_DIR, split, category), exist_ok=True)

def split_data():
    """Split images from raw folder into train/val/test"""
    create_processed_structure()

    for category in ['bread', 'champagnes', 'milk', 'sugar']:
        category_path = os.path.join(RAW_DIR, category)

        if not os.path.exists(category_path):
            print(f"Warning: {category_path} does not exist, skipping...")
            continue

        # Get all image files
        images = [f for f in os.listdir(category_path)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if len(images) == 0:
            print(f"Warning: No images found in {category_path}")
            continue

        print(f"Processing {category}: {len(images)} images")

        # Split: 60% train, 20% val, 20% test
        train_imgs, temp_imgs = train_test_split(images, test_size=0.4, random_state=42)
        val_imgs, test_imgs = train_test_split(temp_imgs, test_size=0.5, random_state=42)

        # Copy files to respective folders
        for img in train_imgs:
            shutil.copy2(
                os.path.join(category_path, img),
                os.path.join(PROCESSED_DIR, 'train', category, img)
            )

        for img in val_imgs:
            shutil.copy2(
                os.path.join(category_path, img),
                os.path.join(PROCESSED_DIR, 'val', category, img)
            )

        for img in test_imgs:
            shutil.copy2(
                os.path.join(category_path, img),
                os.path.join(PROCESSED_DIR, 'test', category, img)
            )

        print(f"  Train: {len(train_imgs)}, Val: {len(val_imgs)}, Test: {len(test_imgs)}")

if __name__ == "__main__":
    print("Splitting raw data into train/val/test folders...")
    split_data()
    print("Data processing complete!")