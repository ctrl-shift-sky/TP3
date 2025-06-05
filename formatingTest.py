def load_html():
    with open('index.html', 'r') as f:
        return f.read()

html_template = load_html()
current_temp = 25
speed = 25
response = html_template.format(temp=current_temp, speed=speed)
with open('output.html', 'w') as f:
    f.write(response)