import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

WIDTH = 128
HEIGHT = 32  # Change to 64 if needed

# --- Setup (runs once, when the file is imported) ---
oled_reset = digitalio.DigitalInOut(board.D17)
spi = board.SPI()
oled_dc = digitalio.DigitalInOut(board.D27)
oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, oled_dc, oled_reset, None)

oled.fill(0)
oled.show()

font = ImageFont.load_default()


# --- Called every time there is new data ---
def draw_centered(draw, text, y):
    """Draw one line of text, centered horizontally, with its top at y."""
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    draw.text(((oled.width - text_width) // 2, y), text, font=font, fill=255)


def refresh_display(data):
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    draw_centered(draw, "waterlevel =", 4)   # top line
    draw_centered(draw, str(data), 18)       # bottom line

    oled.image(image)
    oled.show()

def show_message(text):
    """Show a single centered line, e.g. 'loading data'."""
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    draw_centered(draw, text, 11)   # roughly vertically centered on 32 px
    oled.image(image)
    oled.show()

def refresh_display_drinking(data):
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    draw_centered(draw, str(data), 10)       # bottom line

    oled.image(image)
    oled.show()


def turn_off_display():
    """Clear the screen and switch the OLED off."""
    oled.fill(0)
    oled.show()
    oled.poweroff()