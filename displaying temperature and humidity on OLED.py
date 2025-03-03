print("Hello, ESP32-S3!")

from machine import Pin, I2C, Timer
import machine
import ssd1306
import dht
import time

DHT_PIN = 4  # DHT22 data pin
button = Pin(0, Pin.IN, Pin.PULL_UP)

# Initialize DHT22 sensor
dht_sensor = dht.DHT11(machine.Pin(DHT_PIN))  # Use DHT11 if needed

# Initialize OLED display
i2c = I2C(0, scl=Pin(9), sda=Pin(8))  # Adjust for your ESP32-S3 board
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Check if OLED is detected
print("Scanning I2C bus...")
devices = i2c.scan()
print("Devices found:", devices)
if not devices:
    print("No I2C devices found! Check wiring.")

pressed = False
debounce_timer = None

def button_pressed(pin):
    global debounce_timer, pressed  

    if debounce_timer is None:
        pressed = not pressed
        if pressed:
            oled.poweroff()
        else:
            oled.poweron()
            oled.fill(0)
            oled.text("Display On", 0, 0)
            oled.show()

        debounce_timer = Timer(-1)
        debounce_timer.init(mode=Timer.ONE_SHOT, period=200, callback=debounce_callback)

def debounce_callback(timer):
    global debounce_timer
    debounce_timer = None

# Attach the interrupt to the button's falling edge
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# Main loop
while True:
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        print(f"🌡️ Temp: {temp} C, 💧 Humidity: {humidity}%")
        print("Blow on the sensor and check if values change!")

        oled.fill(0)
        oled.text("🌡️ {} C".format(temp), 0, 0)  # Temperature with emoji
        oled.text("💧 {}%".format(humidity), 0, 16)  # Humidity with emoji
        oled.show()

    except Exception as e:
        print("Error reading DHT22 sensor:", e)
    
    time.sleep(1)  # Update every second

