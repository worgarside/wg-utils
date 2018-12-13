from time import sleep
import pigpio

pi = pigpio.pi()

PIN_OUT = [18, 23, None, 24, None]
PIN_SEQUENCE = [3, 1, 1, 1, 3, 1, 1, 3, 1, 3]


def main():
    for pin in PIN_OUT:
        pi.set_mode(pin, pigpio.OUTPUT)

    for pin_ref in PIN_SEQUENCE:
        pi.write(PIN_OUT[pin_ref], 1)
        sleep(0.05)
        pi.write(PIN_OUT[pin_ref], 0)
        sleep(0.05)

    pi.stop()


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = 'Toggles the laptop screen display source. Requires the circuit created in Schematic.fzz'
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
