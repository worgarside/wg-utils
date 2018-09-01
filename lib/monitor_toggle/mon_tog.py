from time import sleep
import pigpio

pi = pigpio.pi()

PIN_OUT = 26


def main():
    pi.set_mode(PIN_OUT, pigpio.OUTPUT)

    pi.write(PIN_OUT, 1)
    sleep(0.05)
    pi.write(PIN_OUT, 0)
    pi.stop()


def user_help():
    """
    A helper function which outputs any extra information about your script as well as returns expected args
    :returns: a dictionary of argument keys and descriptions to be printed in the same way by every script
    """
    author = 'Will Garside'
    description = 'Toggles the laptop screen. Requires the circuit created in Schematic.fzz'
    expected_args = {}
    env_list = {}

    return author, description, expected_args, env_list


if __name__ == '__main__':
    main()
