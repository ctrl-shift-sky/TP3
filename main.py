from machine import Pin, ADC
import network
import socket
import time
import onewire
import ds18x20
from stepper import Stepper  # Requires Stepper.py library

# Hardware Configuration
TEMP_PIN = Pin(22)  # Assuming DS18B20 on GPIO22
STEP_PINS = [19, 18, 5, 17]  # Adjust based on your wiring

# Initialize components
ow = onewire.OneWire(TEMP_PIN)
ds = ds18x20.DS18X20(ow)
stepper = Stepper(STEP_PINS[0], STEP_PINS[1], STEP_PINS[2], STEP_PINS[3], delay=2)

# WiFi Configuration
ssid = 'TR'
password = '123456789'
wlan = network.WLAN(network.STA_IF)

# State variables
LED1_state = "OFF"
LED2_state = "OFF"
current_temp = "N/A"

def connect_wifi():
    wlan.active(True)
    wlan.connect(ssid, password)
    for _ in range(10):
        if wlan.isconnected():
            print('IP:', wlan.ifconfig()[0])
            return True
        time.sleep(1)
    print('Connection failed')
    return False

def read_temperature():
    try:
        roms = ds.scan()
        ds.convert_temp()
        time.sleep_ms(750)
        return ds.read_temp(roms[0])
    except:
        return None

def load_html():
    with open('index.html', 'r') as f:
        return f.read()
    
html_template = load_html()

temp_value = 23.5 


# Connect to WiFi
if not connect_wifi():
    raise RuntimeError("Network connection failed")

# Set up web server
s = socket.socket()
s.bind(('0.0.0.0', 80))
s.listen(1)

while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()
    
    # Process requests
    if '/LED' in request:
        # Existing LED control logic
        pass
    elif '/stepper/' in request:
        parts = request.split()
        if 'stepper/left' in parts[1]:
            steps = int(parts[1].split('/')[-1])
            stepper.step(-steps)
        elif 'stepper/right' in parts[1]:
            steps = int(parts[1].split('/')[-1])
            stepper.step(steps)
    elif '/refresh' in request:
        current_temp = read_temperature() or "N/A"
        
    response = response = html_template.format(temp=current_temp)
    cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
