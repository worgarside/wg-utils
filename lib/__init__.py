import os
# noinspection PyUnresolvedReferences
from importlib import import_module
import_dict = {}


def walk(top, max_depth):
    dirs, files = [], []

    for name in os.listdir(top):
        (dirs if os.path.isdir(os.path.join(top, name)) else files).append(name)
    yield top, dirs, files
    if max_depth > 1:
        for name in dirs:
            for x in walk(os.path.join(top, name), max_depth - 1):
                yield x


def get_modules():
    dirname, _ = os.path.split(os.path.abspath(__file__))
    exportable_modules = []
    file_loc = '/'.join(__file__.split('/')[:-1])
    if not file_loc:
        file_loc = '\\'.join(__file__.split('\\')[:-1])

    for root, dirs, _ in walk(file_loc, 1):
        for sub_dir in dirs:
            if not sub_dir == '__pycache__':
                for _, _, files in walk(os.path.join(root, sub_dir), 0):
                    for file in files:
                        if file.split('.')[-1] == 'py' and not file == '__init__.py':
                            exportable_modules.append('lib.%s.%s' % (sub_dir, file[:-3]))
    return exportable_modules


exportable_imports = []
modules = get_modules()

for module in modules:
    key = module.split('.')[-1]
    try:
        exec("{}=import_module('{}')".format(key, module))
    except KeyError as key_error:
        if str(key_error) == "'DISPLAY'":
            os.environ['DISPLAY'] = ':0.0'
            modules.append(module)
        else:
            raise KeyError(key_error)
    exportable_imports.append(key)

__all__ = exportable_imports
