import os
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Configuration
BASE_IMAGE_PATH = 'card.png'
# The image is 616x618.
# Quadrants are roughly:
# Top-Left: (0, 0) to (308, 309)
# Top-Right: (308, 0) to (616, 309)
# Bottom-Left: (0, 309) to (308, 618)
# Bottom-Right: (308, 309) to (616, 618)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # 1. Load Base Image
        try:
            base_img = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        except FileNotFoundError:
            return "Base image not found on server.", 500

        # 2. Process Uploaded Photo (Bottom-Left)
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file.filename != '':
                try:
                    photo = Image.open(photo_file).convert("RGBA")
                    # Target size for bottom-left quadrant
                    target_width = 308
                    target_height = 309
                    
                    # Resize/Crop logic to fill the quadrant nicely
                    # We'll use ImageOps.fit or manual resizing to cover the area
                    # For simplicity, let's resize to cover and center crop
                    photo_ratio = photo.width / photo.height
                    target_ratio = target_width / target_height
                    
                    if photo_ratio > target_ratio:
                        # Photo is wider than target
                        new_height = target_height
                        new_width = int(new_height * photo_ratio)
                    else:
                        # Photo is taller than target
                        new_width = target_width
                        new_height = int(new_width / photo_ratio)
                        
                    photo = photo.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Center crop
                    left = (new_width - target_width) / 2
                    top = (new_height - target_height) / 2
                    right = (new_width + target_width) / 2
                    bottom = (new_height + target_height) / 2
                    
                    photo = photo.crop((left, top, right, bottom))
                    
                    # Paste into bottom-left (0, 309)
                    base_img.paste(photo, (0, 309))
                    
                except Exception as e:
                    print(f"Error processing image: {e}")
                    return f"Error processing uploaded image: {e}", 400

        # 3. Process Text (Bottom-Right)
        text = request.form.get('text', '')
        if text:
            text = text[:50]  # Enforce max 50 chars
            draw = ImageDraw.Draw(base_img)
            
            # Define text area in bottom-right
            # (308, 309) to (616, 618)
            # Let's add some padding
            text_area_x = 308 + 20
            text_area_y = 309 + 20
            text_area_w = 308 - 40
            text_area_h = 309 - 40
            
            # Load a font
            try:
                # Try to use a system font or a default one
                # On Mac, Arial or Helvetica usually exists
                font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
                if not os.path.exists(font_path):
                     font_path = "/System/Library/Fonts/Helvetica.ttc"
                font = ImageFont.truetype(font_path, 24)
            except IOError:
                font = ImageFont.load_default()

            # Simple text wrapping could be added here if needed, 
            # but for <50 chars, we might just let it flow or break manually.
            # Let's do a basic wrap.
            
            lines = []
            words = text.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] <= text_area_w:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line))
            
            # Draw text
            y_offset = text_area_y
            # Center vertically in the quadrant? Or just start at top?
            # Let's center vertically for better aesthetics
            total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] for line in lines])
            # Adjust y_offset to center
            y_offset = 309 + (309 - total_text_height) // 2

            for line in lines:
                # Center horizontally
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2]
                x_offset = 308 + (308 - line_width) // 2
                
                # Draw text (white or black? Assuming light background or dark? 
                # Let's use black for now, or maybe white if the card is dark.
                # I'll default to black, but maybe make it configurable or check the card color.
                # Given "robotics", maybe dark theme? I'll stick to black for high contrast on light, 
                # or white on dark. I'll use a safe dark grey/black.)
                draw.text((x_offset, y_offset), line, font=font, fill="black")
                y_offset += bbox[3] + 5 # Line spacing

        # 4. Save to buffer
        img_io = io.BytesIO()
        base_img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)
