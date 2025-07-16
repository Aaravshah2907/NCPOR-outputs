import os
from PIL import Image

# Grid configuration
rows, cols = 3, 4
cell_bg = (255, 255, 255)  # white background

# List your seasons here
seasons = ['Spring', 'Summer', 'Autumn', 'Winter']

# Supported image file extensions
exts = ('.png', '.jpg', '.jpeg')

def make_season_grid(season_folder, output_filename):
    # Gather all image files in the season folder
    image_files = [f for f in os.listdir(season_folder) if f.lower().endswith(exts)]
    image_files.sort()  # Use a specific order if you want; remove or change as needed

    # Open all available images (up to max grid slots)
    images = []
    for f in image_files[:rows * cols]:
        img = Image.open(os.path.join(season_folder, f))
        images.append(img)

    if not images:
        print(f"No images found for {season_folder}")
        return

    # Use the size of the first image as the standard cell size
    cell_width, cell_height = images[0].size

    # Resize others to match the cell size (if needed)
    for i in range(len(images)):
        if images[i].size != (cell_width, cell_height):
            images[i] = images[i].resize((cell_width, cell_height), resample=Image.Resampling.LANCZOS)

    # Create a blank grid image
    grid_img = Image.new('RGB', (cols * cell_width, rows * cell_height), color=cell_bg)

    # Paste images into the grid
    for idx, img in enumerate(images):
        row = idx // cols
        col = idx % cols
        x, y = col * cell_width, row * cell_height
        grid_img.paste(img, (x, y))

    # Save the grid image
    grid_img.save(output_filename)
    print(f"Saved {output_filename}")

# Run for each season
for season in seasons:
    folder = season  # assumes subfolder is named exactly as the season
    output_file = f"{season}.png"
    if os.path.isdir(folder):
        make_season_grid(folder, output_file)
    else:
        print(f"Folder '{folder}' not found, skipping.")


