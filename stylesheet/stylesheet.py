import re
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui     import QFontMetrics
from basics.basic_function import resource_path
from stylesheet.colors import *
from stylesheet.theme import ThemeManager as TM
from stylesheet.theme import THEME_KEYS

# — your existing converters —
def em(val, widget):    return round(val * QFontMetrics(widget.font()).height())
def rem(val):           return round(val * QFontMetrics(QApplication.font()).height())
def ch(val, widget):    return round(val * QFontMetrics(widget.font()).horizontalAdvance("0"))
def ex(val, widget):    return round(val * QFontMetrics(widget.font()).xHeight())
def vw(val, widget):    return round(widget.width()  * (val / 100))
def vh(val, widget):    return round(widget.height() * (val / 100))
def vmin(val, widget):  return round(min(widget.width(), widget.height()) * (val / 100))
def vmax(val, widget):  return round(max(widget.width(), widget.height()) * (val / 100))

# — the stylesheet processor —
_UNIT_PATTERN = re.compile(r'([\d.]+)(em|rem|ch|ex|vw|vh|vmin|vmax)\b')

def process_css(css_text: str, widget: QWidget) -> str:
    """
    Finds all occurrences of e.g. "1.5em", "20vw", etc. in the CSS,
    converts them to px based on the current widget/app metrics,
    and returns a new CSS string with only px values.
    """
    def _repl(match):
        val, unit = match.groups()
        f = float(val)
        # dispatch to the right converter
        if unit == "em":     px = em(f, widget)
        elif unit == "rem":  px = rem(f)
        elif unit == "ch":   px = ch(f, widget)
        elif unit == "ex":   px = ex(f, widget)
        elif unit == "vw":   px = vw(f, widget)
        elif unit == "vh":   px = vh(f, widget)
        elif unit == "vmin": px = vmin(f, widget)
        elif unit == "vmax": px = vmax(f, widget)
        else:                px = f  # shouldn't happen
        return f"{px}px"

    return _UNIT_PATTERN.sub(_repl, css_text)

def load_stylesheet(style_path: str, widget: QWidget=None):
    path = resource_path(style_path)

    with open(path, "r") as file:
        stylesheet = file.read()

    return process_css(stylesheet, widget)

def get_stylesheet(theme: str, subtheme: str='Default') -> str:
    with open(resource_path("assets/style.qss"), "r") as file:
        stylesheet = file.read()

    for key in THEME_KEYS:
        stylesheet = stylesheet.replace(f"${key}$", TM.get(key, theme, subtheme))
    
    stylesheet = stylesheet.replace("$Menu_Hover_BG_Color$", GREY_8)
    stylesheet = stylesheet.replace("$Formulation_BG_Color$", GREY_2)
    stylesheet = stylesheet.replace("$QPushButton_BG_Color$", GREY_8)
    stylesheet = stylesheet.replace("$QPushButton_Color$", BLACK)
    stylesheet = stylesheet.replace("$QPushButtonHover_BG_Color$", GREY_7)

    # print(stylesheet)

    return stylesheet