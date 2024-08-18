from PIL import Image, ImageDraw, ImageFont
import requests
import os, random

def generate_welcome_image(username: str, servername: str, profile_url: str, size=(900,398)):
    W,H = size

    # Create Image & # Add a gradient to the background #0f2027 → #203a43 → #2c5364 
    img = create_three_color_gradient(W, H, [(15, 32, 39), (32, 58, 67), (44, 83, 100)])
    
    # ImageDraw
    draw = ImageDraw.Draw(img)
    
    # Fonts
    welcome_headline = ImageFont.truetype("font/ABeeZee-Regular.otf", 40)
    welcome_sub = ImageFont.truetype("font/ABeeZee-Regular.otf", 20)

    
    # Profile Image in top (url)
    r = requests.get(profile_url)

    profiletemp_filename = genarate_temp_file_name()
    with open(profiletemp_filename, "wb") as f:
        f.write(r.content)
    
    profile_img = Image.open(profiletemp_filename)
    profile_img = profile_img.resize((180, 180))

    # In center top
    img.paste(profile_img, (int((W-180)/2), 20))

    # Delete the temp profile image
    os.remove(profiletemp_filename)

    # Add Welcome text with font-size 40px and bold nice font and place center
    text1 = "Welcome " + username
    _, _, w, h = welcome_headline.getbbox(text1)
    draw.text(((W-w)/2, 250), text1, fill="white", font=welcome_headline, align="center")

    text2 = "to " + servername
    _, _, w, h = welcome_sub.getbbox(text2)
    draw.text(((W-w)/2, 320), text2, fill="white", font=welcome_sub, align="center")

    return img
def create_gradient(width, height, colors):
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[1])
    mask = Image.new('L', (width, height))
    
    for y in range(height):
        for x in range(width):
            mask.putpixel((x, y), int(255 * (y / height)))
    
    base.paste(top, (0, 0), mask)
    
    return base

def create_three_color_gradient(width, height, colors):
    gradient1 = create_gradient(width, height // 2, colors[:2])
    gradient2 = create_gradient(width, height // 2, colors[1:])
    
    final_gradient = Image.new('RGB', (width, height))
    final_gradient.paste(gradient1, (0, 0))
    final_gradient.paste(gradient2, (0, height // 2))
    
    return final_gradient
def genarate_temp_file_name():
    '''
    Genarate random temporary file name
    '''
    return f".temp/{random.randint(1000,9999)}"

if __name__ == "__main__":
    img = generate_welcome_image("Mahib", "TalkServer", "https://cdn.discordapp.com/avatars/1243904331326165113/00bdaf6309d939bafb67acff47720256.png?size=1024")
    img.save('test.png')