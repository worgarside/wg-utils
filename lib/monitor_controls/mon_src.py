from time import sleep
from datetime import datetime

from pigpio import pi, OUTPUT, INPUT

pi = pi()

PIN_IN = 25
PIN_OUT = [18, 23, None, 24, None]
PIN_SEQUENCE = [3, 1, 1, 1, 3, 1, 1, 3, 1, 3]


def main():
    pi.set_mode(PIN_IN, INPUT)

    for pin in PIN_OUT:
        if pin:
            pi.set_mode(pin, OUTPUT)

    while True:
        if pi.read(PIN_IN):
            print(f'Button pressed at {datetime.now()}')
            for pin_ref in PIN_SEQUENCE:
                pi.write(PIN_OUT[pin_ref], 1)
                sleep(0.1)
                pi.write(PIN_OUT[pin_ref], 0)
                sleep(0.4)
            sleep(5)
        sleep(0.1)


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = 'Toggles the laptop screen display source. Requires the circuit created in Schematic_src.fzz'
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
