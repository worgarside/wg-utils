

def styled(*args):

    formats = {
        'UNDERLINE': '\033[4m',
        'BOLD': '\033[1m',
        'YELLOW': '\033[93m',
        'PURPLE': '\033[95m',
        'BLUE': '\033[94m',
        'GREEN': '\033[92m',
        'RED': '\033[91m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'MAGENTA': '\033[95m',
        'GREY': '\033[90m',
        'BLACK': '\033[90m',
        'DEFAULT': '\033[99m',
        'END': '\033[0m'
    }

    format_string = ""
    if type(args[0]) is list:
        args = {*args[0]}

    for kw in args:
        if kw is not None:
            try:
                uc_kw = kw.upper()
                format_string = "{}{code}".format(format_string, code=formats[uc_kw])
            except KeyError:
                # Silently drop unknown keys
                pass
            except AttributeError:
                pass

    return "{}".format(format_string)