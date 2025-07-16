import os
from PIL import Image

# Configuration
folder = 'monthly_images'
year = 7

# Correct month order as per standard abbreviations
months = [
    'jan', 'feb', 'mar', 'apr',
    'may', 'jun', 'jul', 'aug',
    'sep', 'oct', 'nov', 'dec'
]

# Grid configuration (3 rows, 4 columns)
grid_rows = 3
grid_cols = 4

# Collect image paths in monthly order
image_filenames = [
    f"year{year}-{month}-average.png" for month in months
]
image_paths = [os.path.join(folder, fname) for fname in image_filenames]

# Check that all images exist and open them
images = []
for path in image_paths:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing image: {path}")
    images.append(Image.open(path))

# All images must be the same size
img_w, img_h = images[0].size
for img in images:
    if img.size != (img_w, img_h):
        raise ValueError("All images must be the same size.")

# Create the output grid image
grid_img = Image.new('RGB', (grid_cols * img_w, grid_rows * img_h))

# Paste each image into the right place
for idx, img in enumerate(images):
    row = idx // grid_cols
    col = idx % grid_cols
    grid_img.paste(img, (col * img_w, row * img_h))

# Save the grid image
output_path = os.path.join(folder, f'year{year}_monthly_grid.png')
grid_img.save(output_path)
print(f"Grid image saved to {output_path}")

