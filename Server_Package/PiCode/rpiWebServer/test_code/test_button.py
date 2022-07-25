import RPi.GPIO as GPIO

button_pin = 7

def setup():
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    # initialize button pin


def button_callback(channel):
    print("Button was pushed!")

setup()

GPIO.add_event_detect(button_pin, GPIO.RISING, callback=button_callback) # Setup event on pin 10 rising edge
message = input("Press enter to quit\n\n")
GPIO.cleanup() # Clean up
