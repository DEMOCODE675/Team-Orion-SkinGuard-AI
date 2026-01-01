import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
import numpy as np
import os

# Config
IMG_SIZE = 300  # Official EfficientNetB3 input size
BATCH_SIZE = 32
EPOCHS = 15
EPOCHS_FINETUNE = 5  # Fine-tuning epochs

# Paths
TRAIN_DIR = "dataset/train"
VAL_DIR = "dataset/validation"

# Data generators with official EfficientNet preprocessing
train_gen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1
)

val_gen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_data = train_gen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

val_data = val_gen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

# Base model
base_model = EfficientNetB3(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base_model.trainable = False

# Custom head
x = GlobalAveragePooling2D()(base_model.output)
x = Dense(128, activation="relu")(x)
output = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# Callbacks with reduced LR on plateau for better convergence
callbacks = [
    EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
    ModelCheckpoint("skinguard_version_3.h5", monitor="val_loss", save_best_only=True),
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6, verbose=1)
]

# Train with class weights to handle imbalance
print("📊 Computing class weights...")
class_counts = {}
for class_name in os.listdir(TRAIN_DIR):
    class_dir = os.path.join(TRAIN_DIR, class_name)
    count = len([f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))])
    class_counts[class_name] = count
    print(f"  {class_name}: {count}")

total = sum(class_counts.values())
class_weight = {i: total / (len(class_counts) * count) for i, count in enumerate(class_counts.values())}
print(f"✓ Class weights: {class_weight}\n")

# Train
print("🚀 Training base model (frozen backbone)...")
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS,
    callbacks=callbacks,
    class_weight=class_weight
)

print("\n✅ Base model training complete!")
print(f"📁 Model saved as: skinguard_version_3.h5")

# Fine-tuning: unfreeze top layers of base model
print("\n🔄 Fine-tuning: unfreezing top 50 layers...")
base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),  # Lower LR for fine-tuning
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

print("⏱️  Fine-tuning for", EPOCHS_FINETUNE, "epochs...")
history_finetune = model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS_FINETUNE,
    callbacks=callbacks,
    class_weight=class_weight
)

print("\n✅ Fine-tuning complete!")
