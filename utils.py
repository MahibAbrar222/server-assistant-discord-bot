import os
import random

from PIL import Image, ImageDraw, ImageFont
import requests


def generate_welcome_image(username: str, servername: str, profile_url: str, size=(900, 398)):
    """Generate a welcome image with gradient background and profile picture.
    
    Args:
        username: The username to display
        servername: The server name to display
        profile_url: URL to the user's profile picture
        size: Tuple of (width, height) for the image
        
    Returns:
        PIL Image object with the welcome message
    """
    width, height = size

    # Create gradient background
    img = create_three_color_gradient(width, height, [(15, 32, 39), (32, 58, 67), (44, 83, 100)])
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    welcome_headline = ImageFont.truetype("font/ABeeZee-Regular.otf", 40)
    welcome_sub = ImageFont.truetype("font/ABeeZee-Regular.otf", 20)
    
    # Download and add profile image
    response = requests.get(profile_url)
    profile_temp_filename = generate_temp_file_name()
    
    with open(profile_temp_filename, "wb") as f:
        f.write(response.content)
    
    profile_img = Image.open(profile_temp_filename)
    profile_img = profile_img.resize((180, 180))
    img.paste(profile_img, (int((width - 180) / 2), 20))
    os.remove(profile_temp_filename)

    # Add welcome text
    text1 = f"Welcome {username}"
    _, _, text_width, _ = welcome_headline.getbbox(text1)
    draw.text(((width - text_width) / 2, 250), text1, fill="white", font=welcome_headline, align="center")

    text2 = f"to {servername}"
    _, _, text_width, _ = welcome_sub.getbbox(text2)
    draw.text(((width - text_width) / 2, 320), text2, fill="white", font=welcome_sub, align="center")

    return img

def create_gradient(width, height, colors):
    """Create a two-color vertical gradient.
    
    Args:
        width: Width of the gradient
        height: Height of the gradient
        colors: List of two RGB tuples for gradient colors
        
    Returns:
        PIL Image with gradient
    """
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[1])
    mask = Image.new('L', (width, height))
    
    for y in range(height):
        for x in range(width):
            mask.putpixel((x, y), int(255 * (y / height)))
    
    base.paste(top, (0, 0), mask)
    return base


def create_three_color_gradient(width, height, colors):
    """Create a three-color vertical gradient.
    
    Args:
        width: Width of the gradient
        height: Height of the gradient
        colors: List of three RGB tuples for gradient colors
        
    Returns:
        PIL Image with gradient
    """
    gradient1 = create_gradient(width, height // 2, colors[:2])
    gradient2 = create_gradient(width, height // 2, colors[1:])
    
    final_gradient = Image.new('RGB', (width, height))
    final_gradient.paste(gradient1, (0, 0))
    final_gradient.paste(gradient2, (0, height // 2))
    
    return final_gradient


def generate_temp_file_name():
    """Generate a random temporary file name.
    
    Returns:
        String path to a temporary file
    """
    return f".temp/{random.randint(1000, 9999)}"



if __name__ == "__main__":
    img = generate_welcome_image(
        "Mahib", 
        "TalkServer", 
        "https://cdn.discordapp.com/avatars/1243904331326165113/00bdaf6309d939bafb67acff47720256.png?size=1024"
    )
    img.save('test.png')