from machine import Pin
from time import ticks_us, sleep_us, sleep_ms

# Setup for receive
pin_clk  = Pin(18, mode=Pin.IN)
pin_data = Pin(16, mode=Pin.IN)

pin_led  = Pin(25, mode=Pin.OUT)

# Setup for send
pin_send_clk  = Pin(26, mode=Pin.OUT)
pin_send_data = Pin(27, mode=Pin.OUT)

# Other setup for send
#pin_send_clk  = Pin(0, mode=Pin.OUT)
#pin_send_data = Pin(1, mode=Pin.OUT)

# globals for receive
led_toggle = False
data = [0] * 25
data_count = 0
last_rising= ticks_us()

# globals for send
baud = 600
cycle_dur = int(1_000_000 / baud) # length of a cycle in us
half_cycle = int(cycle_dur / 2)
front_porch = cycle_dur * 6

print(f"Setup with baud {baud}, cycle duration {cycle_dur}, half cycle {half_cycle} front porch {front_porch}")

def irq_handler_rising(pin):
    global led_toggle
    global data, data_count
    global last_rising
    
    this_rising = ticks_us()
    if this_rising - last_rising > 100_000:
        data_count = 0
       
    last_rising = this_rising
    
    if data_count <= 25:
        data[data_count] = pin_data.value()
    data_count += 1
    
    if led_toggle:
        led_toggle = False
        pin_led.off()
    else:
        led_toggle = True
        pin_led.on()

def receive():
    global data_count, data
    pin_clk.irq(trigger = Pin.IRQ_RISING, handler = irq_handler_rising)
    pin_led.on()

    try:
        while True:
            if data_count >= 25:
                for x in range(24):
                    print(data[x], end="")
                    if (x + 1) % 8 == 0:
                        print(" ", end ="")
                print()
                data_count = 0
        
    except KeyboardInterrupt:
        pin_led.off()
        
    # remove IRQ driver
    pin_clk.irq(None)


def send_word(word):
    global baud, cycle_dur, half_cycle, front_porch

    pin_send_clk.value(0)
    pin_send_data.value(0)
    
    sleep_us(front_porch)

    for x in range(24):
        pin_send_data.value(word[x])
        sleep_us(100)
        pin_send_clk.value(1)
        sleep_us(half_cycle)
        pin_send_clk.value(0)
        sleep_us(100)
        pin_send_data.value(0)
        sleep_us(half_cycle)
        print(word[x], end="")
        
    pin_send_clk.value(1)
    pin_send_data.value(1)
    print()

def send():
    cmd_off = [0,1,0,1,0,1,0,1,  0,0,0,0,0,0,0,0,  0,1,0,1,0,1,0,1]
    cmd_on  = [0,1,0,1,0,1,0,1,  0,0,0,0,0,0,0,1,  0,1,0,1,0,1,1,0]
    cmd_2   = [0,1,0,1,0,1,0,1,  0,0,0,0,0,0,1,0,  0,1,0,1,0,1,1,1]
    cmd_3   = [0,1,0,1,0,1,0,1,  0,0,0,0,0,0,1,1,  0,1,0,1,1,0,0,0] 
    cmd_4   = [0,1,0,1,0,1,0,1,  0,0,0,0,0,1,0,0,  0,1,0,1,1,0,0,1] 
    cmd_5   = [0,1,0,1,0,1,0,1,  0,0,0,0,0,1,0,1,  0,1,0,1,1,0,1,0]
    cmd_6   = [0,1,0,1,0,1,0,1,  0,0,0,0,0,1,1,0,  0,1,0,1,1,0,1,1]

    # These don't do anything - they are here to test if they did
    cmd_7   = [0,1,0,1,0,1,0,1,  0,0,0,0,0,1,1,1,  0,1,0,1,1,1,0,0]
    cmd_8   = [0,1,0,1,0,1,0,1,  0,0,0,0,1,0,0,0,  0,1,0,1,1,1,0,1]
    cmd_9   = [0,1,0,1,0,1,0,1,  0,0,0,0,1,0,0,1,  0,1,0,1,1,1,1,0]
    cmd_10  = [0,1,0,1,0,1,0,1,  0,0,0,0,1,0,1,0,  0,1,0,1,1,1,1,1]
    cmd_11  = [0,1,0,1,0,1,0,1,  0,0,0,0,1,0,1,1,  0,1,1,0,0,0,0,0]
    cmd_12  = [0,1,0,1,0,1,0,1,  0,0,0,0,1,1,0,0,  0,1,1,0,0,0,0,1]
    cmd_13  = [0,1,0,1,0,1,0,1,  0,0,0,0,1,1,0,1,  0,1,1,0,0,0,1,0]
    cmd_14  = [0,1,0,1,0,1,0,1,  0,0,0,0,1,1,1,0,  0,1,1,0,0,0,1,1]

    cmds = [cmd_off, cmd_on, cmd_2, cmd_3, cmd_4, cmd_5, cmd_6,
            cmd_5, cmd_4, cmd_3, cmd_2, cmd_on, cmd_off]
    #cmds = [cmd_on, cmd_6, cmd_7, cmd_8, cmd_9, cmd_10, cmd_11, cmd_12, cmd_off]

    for cmd in cmds:
        send_word(cmd)
        sleep_ms(1000)

    
    
def send_repeat():
    while True:
        send() 


def create_command(x):
    word = [0] * 24
    byte1 = 0x55
    byte2 = x
    byte3 = 0x55 + x
    print(f" {byte1:08b} {byte2:08b} {byte3:08b}")
    
send_repeat()
#send()   
#receive()


"""
01010101 00000000 01010101 
01010101 00000001 01010110 
01010101 00000010 01010111 
01010101 00000011 01011000 
01010101 00000100 01011001 
01010101 00000101 01011010 
01010101 00000110 01011011 
01010101 00000101 01011010 
01010101 00000100 01011001 
01010101 00000011 01011000 
01010101 00000010 01010111 
01010101 00000001 01010110 
01010101 00000000 01010101
"""
