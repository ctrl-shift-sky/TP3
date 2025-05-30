from machine import Pin
import network
import socket
import time

# Define LED pins
LED1 = Pin(2, Pin.OUT)
LED2 = Pin(23, Pin.OUT)

# Initialize LED states
LED1.value(0)  # OFF
LED2.value(0)  # OFF
LED1_state = "LED 1 is OFF"
LED2_state = "LED 2 is OFF"

# WiFi credentials
ssid = 'TR'
password = '123123123'

wlan = network.WLAN(network.STA_IF)

def connect_wifi():
    wlan.active(True)
    print('Attempting to connect to the network...')
    wlan.connect(ssid, password)
    
    max_wait = 10
    while max_wait > 0 and not wlan.isconnected():
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)
    
    if not wlan.isconnected():
        print('Network Connection has failed')
        return False
    else:
        print('Connected to the network successfully.')
        status = wlan.ifconfig()
        print('Enter this address in browser = ' + status[0])
        return True

# HTML template for the web page
html = """<!DOCTYPE html>
<html>
<head>
    <title>ESP32 LED Controller</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            margin: 50px;
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 500px;
            margin: 0 auto;
        }
        .button { 
            padding: 15px 25px; 
            margin: 10px; 
            font-size: 18px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        .on { 
            background-color: #4CAF50; 
            color: white; 
        }
        .off { 
            background-color: #f44336; 
            color: white; 
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .status {
            font-size: 18px;
            margin: 20px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .led-on {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .led-off {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32 LED Controller</h1>
        
        <div class="status %s">
            <strong>%s</strong>
        </div>
        <div>
            <a href="/LED1/on" class="button on">💡 LED 1 ON</a>
            <a href="/LED1/off" class="button off">🔌 LED 1 OFF</a>
        </div>
        
        <div class="status %s">
            <strong>%s</strong>
        </div>
        <div>
            <a href="/LED2/on" class="button on">💡 LED 2 ON</a>
            <a href="/LED2/off" class="button off">🔌 LED 2 OFF</a>
        </div>
        
        <hr style="margin: 30px 0;">
        <p><small>ESP32 IP: %s</small></p>
    </div>
</body>
</html>
"""

# Connect to WiFi
if not connect_wifi():
    print("Failed to connect to WiFi. Check credentials.")

# Set up socket for web server
try:
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socket reuse
    s.bind(addr)
    s.listen(1)
    print('Web server listening on', addr)
except Exception as e:
    print('Failed to set up server:', e)

# Main server loop
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        print('Request:', request[:100])  # Debug line (first 100 chars)
        
        # Parse the request for LED control
        LED1_on = request.find('/LED1/on')
        LED1_off = request.find('/LED1/off')
        LED2_on = request.find('/LED2/on')
        LED2_off = request.find('/LED2/off')
        
        # Handle LED control
        if LED1_on == 6:
            LED1.value(1)
            LED1_state = "LED 1 is ON"
            LED1_class = "led-on"
            print("LED 1 turned ON")
        elif LED1_off == 6:
            LED1.value(0)
            LED1_state = "LED 1 is OFF"
            LED1_class = "led-off"
            print("LED 1 turned OFF")
        else:
            LED1_class = "led-on" if LED1.value() else "led-off"
            
        if LED2_on == 6:
            LED2.value(1)
            LED2_state = "LED 2 is ON"
            LED2_class = "led-on"
            print("LED 2 turned ON")
        elif LED2_off == 6:
            LED2.value(0)
            LED2_state = "LED 2 is OFF"
            LED2_class = "led-off"
            print("LED 2 turned OFF")
        else:
            LED2_class = "led-on" if LED2.value() else "led-off"
        
        # Get current IP address
        current_ip = wlan.ifconfig()[0]
        
        # Send response
        response = html % (LED1_class, LED1_state, LED2_class, LED2_state, current_ip)
        cl.send('HTTP/1.1 200 OK\r\n')
        cl.send('Content-Type: text/html\r\n')
        cl.send('Connection: close\r\n\r\n')
        cl.sendall(response)
        cl.close()
        
    except OSError as e:
        cl.close()
        print('Connection closed due to error:', e)
    except Exception as e:
        cl.close()
        print('Unexpected error:', e)
