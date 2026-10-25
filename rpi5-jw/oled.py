from re import S

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

def refresh_dislpay(data):
    # Define the Reset Pin
    oled_reset = digitalio.DigitalInOut(board.D17)
    # Change these
    # to the right size for your display!
    WIDTH = 128
    HEIGHT = 32 # Change to 64 if needed
    BORDER = 5
    # Use for SPI
    spi = board.SPI()
    oled_dc = digitalio.DigitalInOut(board.D27)
    oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset,None)
    # Clear display.
    oled.fill(0)
    oled.show()
    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)


    # Load default font.
    font = ImageFont.load_default()
    # Draw Some Text
    text = f"waterlevel = {data}"
    bbox = font.getbbox(text)
    (font_width, font_height) = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
    (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
    text,
    font=font,
    fill=255,
    )
    # Display image
    oled.image(image)
    oled.show()