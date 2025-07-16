import os
import re
from PIL import Image

# Configuration
folder_x = 'LCS-seasons-images'
folder_y = 'Image_output'
season_order = ['Spring', 'Summer', 'Autumn', 'Winter']  # chronological order

# Regex to match filenames like 'Spring-2024.png'
pattern = re.compile(r'^(Spring|Summer|Autumn|Winter)-(\d{4})\.png$', re.IGNORECASE)

# Helper: build dict {(season, year): path}
def collect_images(folder):
    file_map = {}
    for fname in os.listdir(folder):
        m = pattern.match(fname)
        if m:
            season = m.group(1).capitalize()  # Normalize
            year = int(m.group(2))
            file_map[(season, year)] = os.path.join(folder, fname)
    return file_map

img_map_x = collect_images(folder_x)
img_map_y = collect_images(folder_y)

# Gather all (season, year) pairs present in BOTH folders, in chronological order
all_pairs = sorted(
    set(img_map_x.keys()) & set(img_map_y.keys()),
    key=lambda pair: (pair[1], season_order.index(pair[0]))
)

# Build GIF frames
frames = []
for season, year in all_pairs:
    im_x = Image.open(img_map_x[(season, year)])
    im_y = Image.open(img_map_y[(season, year)])

    # Make sure heights match, resize Y if needed
    if im_x.size[1] != im_y.size[1]:
        new_width = int(im_y.size[0] * im_x.size[1] / im_y.size[1])
        im_y = im_y.resize((new_width, im_x.size[1]), resample=Image.Resampling.LANCZOS)
    # Composite image side-by-side
    total_width = im_x.size[0] + im_y.size[0]
    combined = Image.new('RGB', (total_width, im_x.size[1]))
    combined.paste(im_x, (0, 0))
    combined.paste(im_y, (im_x.size[0], 0))
    frames.append(combined)

# Save the GIF
if frames:
    frames[0].save(
        'seasonal_comparison.gif',
        save_all=True,
        append_images=frames[1:],
        format='GIF',
        duration=600,
        loop=0
    )
    print("seasonal_comparison.gif created.")
else:
    print("No matching images found in both folders for the given format and order.")

