#! /usr/bin/env python

import sys, re

COLOR_RE = re.compile(r'\033\[([0-9;]*)m')
COLORS_NOT_SUPPORTED = False

if sys.platform == 'win32':
    import collections
    
    try:
        import ctypes
        GetStdHandle = ctypes.windll.kernel32.GetStdHandle
        SetConsoleTextAttribute = ctypes.windll.kernel32.SetConsoleTextAttribute
        GetConsoleScreenBufferInfo = ctypes.windll.kernel32.GetConsoleScreenBufferInfo
    except (ImportError, WindowsError, AttributeError):
        COLORS_NOT_SUPPORTED = True
    else:
        # Windows structures we'll need later
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class SMALL_RECT(ctypes.Structure):
            _fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short), 
                ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.c_short), ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD)]
        
        def GetConsoleTextAttribute(handle):
            info = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(handle, ctypes.byref(info))
            return info.wAttributes
        
        WIN_COLORS_MAP = {
            '1':  (0x08, 0xF7), # bright foreground
            '2':  (0x00, 0xF7), # dark foreground
            '5':  (0x80, 0x7F), # bright background
            '30': (0x00, 0xF8), # black foreground
            '31': (0x04, 0xF8), # red foreground 
            '32': (0x02, 0xF8), # green foreground
            '33': (0x06, 0xF8), # yellow foreground
            '34': (0x01, 0xF8), # blue foreground 
            '35': (0x05, 0xF8), # magenta foreground
            '36': (0x03, 0xF8), # cyan foreground
            '37': (0x07, 0xF8), # white foreground
            '40': (0x00, 0x8F), # black background
            '41': (0x40, 0x8F), # red background
            '42': (0x20, 0x8F), # green background
            '43': (0x60, 0x8F), # yellow background
            '44': (0x20, 0x8F), # blue background
            '45': (0x50, 0x8F), # magenta background
            '46': (0x30, 0x8F), # cyan background
            '47': (0x70, 0x8F), # white background
        }
        WIN_COLORS_MAP = collections.defaultdict(lambda: (0x00, 0xFF), WIN_COLORS_MAP)
        WIN_STDIN_HANDLE = -10
        WIN_STDOUT_HANDLE = -11
        WIN_STDERR_HANDLE = -12
        WIN_HANDLES = {
            sys.stdin: GetStdHandle(WIN_STDIN_HANDLE),
            sys.stdout: GetStdHandle(WIN_STDOUT_HANDLE),
            sys.stderr: GetStdHandle(WIN_STDERR_HANDLE),
        }


class ColoredOutput(object):
    def __init__(self, output_stream):
        self.skip_colors = COLORS_NOT_SUPPORTED
        self.output_stream = output_stream
    
    # 'skip_color' property.
    def get_skip_colors(self):
        return self.__skip_colors
    def set_skip_colors(self, value):
        self.__skip_colors = value
        if value:
            setattr(self, 'write', self.write_no_colors)
        else:
            setattr(self, 'write', self.write_with_colors)
    skip_colors = property(get_skip_colors, set_skip_colors)

    def write_no_colors(self, data):
        self.__output_stream.write(COLOR_RE.sub('', data))

    def get_output_stream(self):
        return self.__output_stream

    if sys.platform == 'win32':
        def set_output_stream(self, value):
            self.__output_stream = value
            self.skip_colors = self.without_colors(value)
            if not self.skip_colors:
                self.__win_handle = WIN_HANDLES[self.output_stream]
                self.win_default_color = GetConsoleTextAttribute(self.__win_handle)

        def without_colors(self, stream):
            return not (stream in WIN_HANDLES and stream.isatty())
        
        def write_with_colors(self, data):
            c = GetConsoleTextAttribute(self.__win_handle)
            color = False
            for chunk in COLOR_RE.split(data):
                if color:
                    for attr in chunk.split(';'):
                        if attr in ['', '0']:
                            c = self.win_default_color # reset to saved color.
                        elif attr == '7':
                            c = (c << 4 | c >> 4) & 0xFF # reverse colors.
                        else:
                            value, mask = WIN_COLORS_MAP[attr]
                            c = (c & mask) | value
                    SetConsoleTextAttribute(WIN_HANDLES[self.output_stream], c)
                else: 
                    self.output_stream.write(chunk)
                color = not color
    else:
        def set_output_stream(self, value):
            self.__output_stream = value
            self.skip_colors = self.without_colors(value)

        def without_colors(self, stream):
            return not stream.isatty()
        
        def write_with_colors(self, data):
            self.output_stream.write(data)
    
    output_stream = property(get_output_stream, set_output_stream)

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.write('\033[m')


if __name__ == '__main__':
    out = ColoredOutput(sys.stdout)
    print>>out, '\033[2;31mhello'
    print>>out, '\033[1;37;5;40msomesome\033[m'
