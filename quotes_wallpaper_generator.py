#!/usr/bin/env python3
import re
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ----------------- CONFIGURATION -----------------
# Image dimensions (1920x1080 → 16:9)
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

# Background color (AMOLED black) and text color
BACKGROUND_COLOR = (0, 0, 0)         # Black
TEXT_COLOR = (255, 255, 255)         # White

# Adjustable padding (in pixels)
PADDING_LEFT = 100
PADDING_RIGHT = 100
PADDING_TOP = 100
PADDING_BOTTOM = 100

# Font configuration
# Provide the absolute path to a valid TTF font file.
# Example for Linux: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Example for Windows: "C:/Windows/Fonts/arial.ttf"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Maximum starting font size; the script will reduce it if the quote does not fit.
MAX_FONT_SIZE = 80
MIN_FONT_SIZE = 20
LINE_SPACING = 1.2  # 20% extra spacing between lines

# Output directory for wallpapers
OUTPUT_DIR = "wallpapers"
# --------------------------------------------------

def get_text_size(draw, text, font):
    """
    Helper function to calculate the width and height of text using textbbox.
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height

def wrap_text(text, draw, font, max_width):
    """
    Wraps text so that each line does not exceed max_width (in pixels)
    using the given draw object and font.
    Returns a list of lines.
    """
    words = text.split()
    if not words:
        return [""]
    
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        test_line = current_line + " " + word
        line_width, _ = get_text_size(draw, test_line, font)
        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def get_fitting_font_and_lines(text, max_width, max_height, draw):
    """
    Starting from MAX_FONT_SIZE, reduce the font size until the wrapped text
    fits into the provided max_width and max_height.
    Returns (font, wrapped_lines).
    """
    font_size = MAX_FONT_SIZE
    font = ImageFont.truetype(FONT_PATH, font_size)
    
    while font_size >= MIN_FONT_SIZE:
        lines = wrap_text(text, draw, font, max_width)
        # Compute total height of text block
        line_heights = [get_text_size(draw, line, font)[1] for line in lines]
        total_height = int(sum(line_heights) * LINE_SPACING)
        if total_height <= max_height:
            return font, lines
        # Reduce font size and try again
        font_size -= 2
        font = ImageFont.truetype(FONT_PATH, font_size)
    
    # If nothing fits, return the smallest font and wrapped lines
    return font, wrap_text(text, draw, font, max_width)

def create_wallpaper(quote, output_path):
    # Create a new image with AMOLED black background
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    
    # Calculate available width and height for text (inside padding)
    available_width = IMAGE_WIDTH - PADDING_LEFT - PADDING_RIGHT
    available_height = IMAGE_HEIGHT - PADDING_TOP - PADDING_BOTTOM
    
    # Get a font that fits and the wrapped lines
    font, lines = get_fitting_font_and_lines(quote, available_width, available_height, draw)
    
    # Calculate total height of text block (with extra line spacing)
    line_heights = [get_text_size(draw, line, font)[1] for line in lines]
    total_text_height = int(sum(line_heights) * LINE_SPACING)
    
    # Starting y coordinate to center vertically
    current_y = PADDING_TOP + (available_height - total_text_height) // 2
    
    # Draw each line centered horizontally
    for line, lh in zip(lines, line_heights):
        line_width, _ = get_text_size(draw, line, font)
        x = PADDING_LEFT + (available_width - line_width) // 2
        draw.text((x, current_y), line, font=font, fill=TEXT_COLOR)
        current_y += int(lh * LINE_SPACING)
    
    # Save the wallpaper image
    image.save(output_path)
    print(f"Wallpaper saved to: {output_path}")

def extract_quotes_from_file(file_path):
    """
    Reads the file and extracts quotes.
    Only lines that start with a number followed by a period are considered.
    Lines starting with '#' or empty lines are ignored.
    Removes surrounding quotation marks if present.
    """
    quotes = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or set(line) == set("-"):
                continue
            # Match a line starting with digits and a dot (e.g., "1. Quote")
            match = re.match(r"^\d+\.\s*(.*)", line)
            if match:
                quote_text = match.group(1).strip()
                # Remove surrounding quotes if they exist
                quote_text = quote_text.strip('"').strip("'")
                if quote_text:
                    quotes.append(quote_text)
    return quotes

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quote_wallpaper_generator.py <input_quotes_file.txt>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    quotes = extract_quotes_from_file(input_file)
    
    if not quotes:
        print("No quotes found in the file.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate a wallpaper for each quote
    for idx, quote in enumerate(quotes, start=1):
        output_file = os.path.join(OUTPUT_DIR, f"quote_{idx}.png")
        create_wallpaper(quote, output_file)

if __name__ == "__main__":
    main()

