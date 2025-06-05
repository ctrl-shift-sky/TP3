from machine import Pin, Timer
import network
import socket
import time
import onewire
import ds18x20

TEMP_PIN = Pin(22) 
STEP_PIN = Pin(19, Pin.OUT)  
DIR_PIN = Pin(18, Pin.OUT)   

ow = onewire.OneWire(TEMP_PIN)
ds = ds18x20.DS18X20(ow)

ssid = 'TR'
password = '123456789'
wlan = network.WLAN(network.STA_IF)

current_temp = "N/A"
speed = 10         
direction = 1      

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

stepper_timer = Timer(-1)
step_state = 0

def stepper_pulse(timer):
    global step_state
    STEP_PIN.value(1)
    time.sleep_us(2) 
    STEP_PIN.value(0)
    step_state ^= 1

def update_stepper():
    DIR_PIN.value(direction)
    if speed > 0:
        period = int(1000 / speed)
        stepper_timer.init(period=period, mode=Timer.PERIODIC, callback=stepper_pulse)
    else:
        stepper_timer.deinit()

if not connect_wifi():
    raise RuntimeError("Network connection failed")
update_stepper()

s = socket.socket()
s.bind(('0.0.0.0', 80))
s.listen(1)

while True:
    cl, addr = s.accept()
    request = cl.recv(1024).decode()
    if '/stepper/speed' in request:
        try:
            idx = request.find('value=')
            if idx != -1:
                val_str = request[idx+6:].split('&')[0].split(' ')[0]
                new_speed = int(val_str)
                if 1 <= new_speed <= 1000:
                    speed = new_speed
                    update_stepper()
        except:
            pass
    if '/stepper/direction' in request:
        if 'dir=0' in request:
            direction = 0
            update_stepper()
        elif 'dir=1' in request:
            direction = 1
            update_stepper()
    if '/refresh' in request:
        current_temp = read_temperature() or "N/A"
    response = html_template.format(temp=current_temp, speed=speed)

    """
    for testing the html
    with open('output.html', 'w') as f:
        f.write(response) 
    """
    cl.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    cl.send(response)
    cl.close()
