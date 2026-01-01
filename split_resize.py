import os
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

# Paths
IMAGE_DIR = "HAM10000_images"
CSV_PATH = "HAM10000_metadata.csv"
OUTPUT_DIR = "dataset"

IMG_SIZE = (300, 300)
# Load CSV
df = pd.read_csv(CSV_PATH)

# ✅ Medically correct mapping
malignant = ['mel', 'bcc', 'akiec']
df['label'] = df['dx'].apply(lambda x: 'malignant' if x in malignant else 'benign')

# Split
train_df, temp_df = train_test_split(
    df, test_size=0.3, stratify=df['label'], random_state=42
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42
)

# Save images
def save_images(dataframe, split_name):
    for _, row in dataframe.iterrows():
        img_name = row['image_id'] + ".jpg"
        label = row['label']

        # find image in either folder
        src_path = None
        for folder in [IMAGE_DIR]:
            temp = os.path.join(folder, img_name)
            if os.path.exists(temp):
                src_path = temp
                break

        if src_path is None:
            continue

        dest_dir = os.path.join(OUTPUT_DIR, split_name, label)
        os.makedirs(dest_dir, exist_ok=True)

        try:
            img = Image.open(src_path).convert("RGB")
            img = img.resize(IMG_SIZE)
            img.save(os.path.join(dest_dir, img_name))
        except Exception as e:
            print("Error:", e)

# Run
save_images(train_df, "train")
save_images(val_df, "validation")
save_images(test_df, "test")

print("✅ Dataset split & resized successfully!")
