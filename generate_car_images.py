from PIL import Image, ImageDraw, ImageFont
import os

def create_car_image(brand, model, save_path):
    # Create a 800x600 image with a gradient background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple gradient background
    for y in range(height):
        r = int(255 * (1 - y/height))
        g = int(200 * (1 - y/height))
        b = int(220 * (1 - y/height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add car brand and model text
    text = f"{brand}\n{model}"
    draw.text((width/2, height/2), text, fill='black', anchor="mm", align="center")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save the image
    image.save(save_path, 'JPEG', quality=95)

def main():
    car_data = [
        ('Toyota', ['Camry', 'Corolla', 'Land Cruiser']),
        ('Chevrolet', ['Malibu', 'Captiva', 'Tracker']),
        ('Hyundai', ['Sonata', 'Tucson', 'Santa Fe']),
        ('BMW', ['X5', '520i', 'X7']),
        ('Mercedes-Benz', ['E200', 'GLE', 'S500']),
    ]
    
    for brand, models in car_data:
        for model in models:
            filename = f"{brand}_{model}.jpg".lower().replace(' ', '_')
            save_path = os.path.join('media', 'car_photos', '2023', '05', filename)
            create_car_image(brand, model, save_path)
            print(f"Created image for {brand} {model}")

if __name__ == '__main__':
    main()
