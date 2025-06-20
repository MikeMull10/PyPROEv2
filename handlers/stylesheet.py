import sys
import os

PALETTES = {
    "White": "white",
    "Dark": "dark",
    "Navy": "styles",
    "Crimson": "crimson",
    "Raspberry": "raspberry",
    "Neon": "neon",
}

NEON_COLORS = {
    "Red": ["#FF3A2C", "#ffabab"],
    "Orange": ["#FF7E33", "#ffa778"],
    "Yellow": ["#F9FF42", "#fcffab"],
    "Green": ["#36BF63", "#abffaf"],
    "Blue": ["#4DDEEE", "#abf1ff"],
    "Royal Blue": ["#4169E1", "#ABBFFF"],
    "Purple": ["#B344EB", "#caabff"],
    "Pink": ["#F043C7", "#ff78e8"],
}

ICON_COLORS = {
    "Neon Red": "#FF3A2C",
    "Neon Orange": "#FF7E33",
    "Neon Yellow": "#F9FF42",
    "Neon Green": "#36BF63",
    "Neon Blue": "#4DDEEE",
    "Neon Royal Blue": "#4169E1",
    "Neon Purple": "#B344EB",
    "Neon Pink": "#F043C7",
    "White": "#141416",
    "Dark": "#FFFFFF"
}

def get_icon_color(theme, subtheme):
    search = theme
    if theme == "Neon":
        search += f" {subtheme}"
    
    return ICON_COLORS.get(search, "#FFFFFF")

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller bundled executables. """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller stores files in a temporary folder (_MEIPASS) during execution
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Load the stylesheet and replace paths with dynamic ones
def load_stylesheet(palette: str="Navy", color: str="", sizes: dict={}):
    stylesheet_path = resource_path(f"assets/{PALETTES.get(palette, 'styles')}{'2' if palette in ['White', 'Dark'] and color == 'Simplified' else ''}.qss")

    with open(stylesheet_path, "r") as file:
        stylesheet = file.read()

    # Replace relative paths in the QSS file with absolute paths
    stylesheet = stylesheet.replace(
        "url(assets/caret-down.svg)", 
        f"url({resource_path('assets/caret-down.svg').replace(os.sep, '/')})"
    )
    stylesheet = stylesheet.replace(
        "url(assets/caret-up.svg)", 
        f"url({resource_path('assets/caret-up.svg').replace(os.sep, '/')})"
    )
    chev_down = f"assets/{'' if palette in ['White', 'Navy'] else 'white-'}chevron-down-solid.svg"
    stylesheet = stylesheet.replace(
        "url(assets/chevron-down-solid.svg)", 
        f"url({resource_path(chev_down).replace(os.sep, '/')})"
    )
    chev_right = f"assets/{'' if palette in ['White', 'Navy'] else 'white-'}chevron-right-solid.svg"
    stylesheet = stylesheet.replace(
        "url(assets/chevron-right-solid.svg)", 
        f"url({resource_path(chev_right).replace(os.sep, '/')})"
    )

    if palette == "Neon" and color in NEON_COLORS.keys():
        stylesheet = stylesheet.replace("$PRIMARY$", NEON_COLORS[color][0])
        stylesheet = stylesheet.replace("$SECONDARY$", NEON_COLORS[color][1])

    for s in ["ButtonSize", "LabelSize", "BoxSize", "TextEditSize"]:
        stylesheet = stylesheet.replace(f"${s}$", f"{int(sizes.get(s, 12))}")
    
    return stylesheet