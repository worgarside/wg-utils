import os
import re
from .terminal import styled

def dict_value_from_case_insensitive_key(d, lookup):
    try:
        # Lookup key matched on lower value
        return d[lookup.lower()]
    except KeyError:
        try:
            # Lookup key matched on uppercase values
            return d[lookup.upper()]
        except KeyError:
            # They key is not in the dict so raise Key Error!
            raise KeyError("Item not found in mapped options. This shouldn't really happen")


class RangeError(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class OptionValidator(object):

    allowed_chars = []
    allowed_range = []

    def validate(self, choice):

        try:
            # Try and make choice into a number
            int_choice = int(choice)

            if self.allowed_range[0] <= int_choice <= self.allowed_range[1]:
                return int_choice
            else:
                raise RangeError(message="The value entered is out of the allowed range")

        except ValueError:
            # Can't be changed into a number
            # Check it's in the allowed list
            if choice.upper() in map(str.upper, self.allowed_chars):
                return choice
            else:
                raise RangeError(message="The value entered is out of the allowed range")


    def __init__(self, allowed_chars=None, allowed_range=None):
        self.allowed_chars = allowed_chars
        self.allowed_range = allowed_range


def pick_database(list, mapped_opts= None, title=None, text=None, clear=False):
    """
    Creates a list of options and picker dialog
    :param list: List of strings to be output 1-x as options
    :param mapped_opts: list of options mapped to strings eg: { "n" : "New", "d" : "Delete }
    :param title: Title for the box
    :param text: Text for the box
    :param clear: Clear the screen before displaying options
    :return: The option selected as a string eg: "New" or "database name"
    """

    # If clear screen before display
    if clear:
        os.system('cls' if os.name == 'nt' else 'clear')

    if title and text:
        box(
            title=title,
            text=text,
            vpad=1,
            border="~",
        )

    # Create list of mapped options and output first
    mapped_allowed_opts = []
    mapped_option_string = ""

    if mapped_opts:
        for value, opt in mapped_opts.items():
            num = "{}".format(opt)
            line_len = 7 - len(num)
            print("{}.{} {}".format(value, "_" * line_len, opt))

            mapped_allowed_opts.append(value)
            # mapped_option_string += "{},".format(value)

        mapped_option_string = ", ".join(mapped_opts)
        mapped_option_string += " or "
        print("...")

    # Output the main list
    list_length = len(list)
    for idx, db in enumerate(list):
        num = "{}".format(idx)
        num_length = len(num)
        line_len = 7 - num_length
        print("{}.{} {}".format(idx + 1, "_" * line_len,  db))

    # Wait for correct answer
    validator = OptionValidator(
        allowed_chars=mapped_allowed_opts,
        allowed_range=[1, list_length]
    )

    while True:

        formatted_string = {
            "f": styled("bold"),
            "length": list_length,
            "opts": mapped_option_string,
            "e": styled("end")
        }

        database_choice_str = input("\n{f}Select option [ {opts} 1-{length} ]{e}:".format(**formatted_string))

        try:
            cleaned = validator.validate(database_choice_str)

            if isinstance(cleaned, int):
                # Lookup choice by index (0 based)
                database_choice = list[int(cleaned) - 1]
            else:
                # Lookup key case insensitve because users!!
                database_choice = dict_value_from_case_insensitive_key(mapped_opts, cleaned)
            break
        except RangeError:
            error_message = {
                "f": styled("bold", "red"),
                "selected": database_choice_str,
                "e": styled("end")
            }
            print("{f}\"{selected}\" is not a valid option!{e}".format(**error_message))
            continue

    # Return string of chosen option eg: "database_name"
    return database_choice


def confirm_dialog(msg="Confirm?"):
    """
    Renders a message and waits for a Y/n confirm from user
    :param msg: string message that is shown in the dialog
    :return: string for the the answer
    """
    options=['Y', 'n']

    options_string = "\033[1m[{}]\033[0m:".format("/".join(options))

    while True:
        try:
            choice = input("{} {}".format(msg, options_string))
        except ValueError:
            print("Incorrect option")
            continue

        if not any(choice.lower() in s.lower() for s in options):
            print("Please select an option: {}".format(options_string))
            continue

        else:
            break

    return choice


def prompt_name(msg, human_rules = "A-Za-z0-9", regex = '^[A-Za-z0-9_]{1,}$'):
    """
    Prompt for a unicode
    :param msg:
    :param human_rules:
    :param regex:
    :return:
    """

    while True:
        try:
            choice = input("\033[1m{} [{}]:\033[0m".format(msg, human_rules))
        except ValueError:
            print("Incorrect option")
            continue

        db_name_pattern = re.compile(regex)

        if not db_name_pattern.match(choice):
            print("Please use the naming convention: {}".format(human_rules))
            continue

        else:
            break

    return choice


import math
import textwrap


def cap_line(string="", caps="#", length=40, color=None):
    """
    Takes a string and adds line caps to the end after centering text
    """
    str_len = len(string)

    l_space = (length - 2- str_len ) // 2
    r_space = int(math.ceil((length - 2 - str_len) / 2))

    l_pad = " " * l_space
    r_pad = " " * r_space

    if color:
        string = "{}{}\033[0m".format(color, string)

    return "{}{}{}{}{}".format(caps, l_pad, string, r_pad, caps)


class GUI():

    clear = True

    bordered = True
    border_style = "#"
    width = 70

    buffer = []

    def line_length(self):
        return self.width - 2 - (self.line_padding * 2) # 2 for the borders

    def add_ends(self, content=None, styles=None):

        if not self.bordered:
            # Don't draw a border!
            return content
        else:
            available_line_length = self.line_length()
            if content is None or content == "":
                # draw full spaced line
                spacer = " " * self.line_padding
                return "{cap}{spacer}{content}{spacer}{cap}".format(cap=self.border_style, spacer=spacer, content=" " * available_line_length)
            else:
                # Workout space and center
                space_after_content = available_line_length - len(content) # TODO: Unicode chars are a problem

                l_space = int(math.floor(space_after_content / 2))
                r_space = int(math.ceil(space_after_content / 2))


                line = {
                    'cap': self.border_style,
                    'l': " " * l_space,
                    'r': " " * r_space,
                    'style': styled(styles),
                    'content': content,
                    'end': styled("end"),
                    'spacer': " " * self.line_padding
                }

                x= "{cap}{spacer}{l}{style}{content}{end}{r}{spacer}{cap}".format(**line)
                return x

    def clear_screen(self):
        if self.clear:
            os.system('cls' if os.name == 'nt' else 'clear')

    def border(self):
        self.buffer.append( "{}".format(self.border_style * self.width) )

    def lines(self, count=1):
        for l in range(count):
            self.buffer.append(self.add_ends())

    def content(self, content, styles=None):

        if type(content) is list:
            # If a list then unwrap
            for li in content:
                self.content(li, styles=styles)
        elif type(content) is str:
            # If string
            if len(content) > self.line_length():
                # If longer than a line then split
                split_lines = textwrap.wrap(content, self.line_length())
                self.content(split_lines, styles=styles)
            else:
                # Just render it
                self.buffer.append(self.add_ends(content=content, styles=styles))

    def draw(self):
        # Clear screen
        self.clear_screen()

        # Draw buffer
        for l in self.buffer:
            print(l)

        # Clear buffer
        self.screen = []

    def space_after(self, lines):
        for l in range(lines):
            self.buffer.append("") #Print always adds a new line so no need to break line!

    def __init__(self, width, bordered=True, border_style="#", line_padding=10):
        self.width = width
        self.bordered = bordered
        self.border_style = border_style
        self.line_padding = line_padding


def box(title="", text="", width=70, vpad=2, h_pad=10, border="#", clear=False):

    gui = GUI(width=60)
    gui.border()
    gui.lines(vpad)
    gui.content(title, styles=['UNDERLINE', 'bold', 'yellow'])
    gui.lines(1)
    gui.content(text, styles='PURPLE')
    gui.lines(vpad)
    gui.border()
    gui.space_after(2)

    gui.draw()
