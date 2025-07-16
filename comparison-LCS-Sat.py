from PIL import Image, ImageDraw, ImageFont
import os

def combine_images_grid():
    seasons = ['Summer', 'Spring', 'Autumn', 'Winter']
    folders = ['LCS-seasons-images', 'Image_output']
    years_ranges = [(2011, 2016), (2017, 2022)]
    images_per_row = 4
    images_per_col = 3

    # Font for title
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    for season in seasons:
        for year_init, year_final in years_ranges:
            grid_images = []
            missing_files = []

            # 1. Find max width and height of images in both folders for the current season and year range
            max_width = 0
            max_height = 0
            for year in range(year_init, year_final + 1):
                for folder in folders:
                    file_path = os.path.join(folder, season, f"{season}-{year}.png")
                    if os.path.exists(file_path):
                        img = Image.open(file_path)
                        max_width = max(max_width, img.width)
                        max_height = max(max_height, img.height)

            if max_width == 0 or max_height == 0:
                max_width, max_height = 200, 200  # Default size if no images found

            # 2. Load and resize images (or create blank if missing)
            for year in range(year_init, year_final + 1):
                for folder in folders:
                    file_path = os.path.join(folder, season, f"{season}-{year}.png")
                    if os.path.exists(file_path):
                        img = Image.open(file_path)
                        img = img.resize((max_width, max_height), Image.LANCZOS)
                        grid_images.append(img)
                    else:
                        missing_files.append(file_path)
                        blank_img = Image.new('RGB', (max_width, max_height), color='white')
                        grid_images.append(blank_img)

            if missing_files:
                print(f"Missing files for {season} {year_init}-{year_final}:")
                for mf in missing_files:
                    print(mf)

            combined_width = images_per_row * max_width
            combined_height = images_per_col * max_height + 50  # Extra space for title
            combined_img = Image.new('RGB', (combined_width, combined_height), color='white')

            draw = ImageDraw.Draw(combined_img)
            title = f"{season} {year_init}-{year_final} Comparison"
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text(((combined_width - text_width) / 2, 10), title, fill='black', font=font)

            for idx, img in enumerate(grid_images):
                x = (idx % images_per_row) * max_width
                y = (idx // images_per_row) * max_height + 50
                combined_img.paste(img, (x, y))

            output_filename = f"Comparison/{season}_Comparison_{year_init}_{year_final}.png"
            combined_img.save(output_filename)
            print(f"Saved combined image: {output_filename}")

combine_images_grid()
