from stylesheet.colors import *

"""
Themes: 'Light', 'Dark'
Colors: 'Red', 'Orange', 'Yellow', 'Green', 'Light Blue', 'Blue', 'Purple', 'Pink'
"""
THEME = {
    "Base_BG_Color": {
        'Light': GREY_8,
        'Dark':  GREY_0,
    },
    "Base_Color": {
        'Light': BLACK,
        'Dark':  WHITE,
    }
}

THEME_KEYS = list(THEME.keys())

class ThemeManager:
    @staticmethod
    def get(key: str, theme: str='Light', color='Red'):
        start = THEME.get(key, None)
        if not start:
            return None
        
        placeholder = start
        while True:
            res = placeholder.get(theme, placeholder.get(color, None))

            if type(res) == dict:
                placeholder = res
                continue

            return res

if __name__ == "__main__":
    print(ThemeManager.get('Base_BG_Color', 'Light', None))
