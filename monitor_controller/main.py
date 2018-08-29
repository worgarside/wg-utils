from time import sleep
import pigpio

pi = pigpio.pi()

PINOUT = 26

pi.set_mode(PINOUT, pigpio.OUTPUT)

pi.write(PINOUT, 1)
sleep(0.05)
pi.write(PINOUT, 0)
pi.stop()
