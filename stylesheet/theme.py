from stylesheet.colors import *

"""
Themes: 'Light', 'Dark'
Colors: 'Red', 'Orange', 'Yellow', 'Green', 'Light Blue', 'Blue', 'Purple', 'Pink'
"""
THEME = {
    "Base_BG_Color": {
        'Light': GREY_8,
        'Dark':  GREY_VS,
    },
    "Base_Color": {
        'Light': BLACK,
        'Dark':  WHITE,
    },
    "Btn_Opt_Start_BG": {
        'Light': {
            'Default': GREY_8,
            'Red'    : RED_VIVID_4,
            'Orange' : ORANGE_VIVID_4,
            'Yellow' : YELLOW_VIVID_4,
            'Green'  : GREEN_VIVID_3,
            'Light Blue': BLUE_VIVID_5,
            'Blue'   : BLUE_VIVID_3,
            'Purple' : PURPLE_VIVID_3,
            'Pink'   : PINK_VIVID_6,
        },
        'Dark': {
            'Default': GREY_2,
            'Red'    : RED_4,
            'Orange' : ORANGE_4,
            'Yellow' : YELLOW_4,
            'Green'  : GREEN_4,
            'Light Blue': BLUE_7,
            'Blue'   : BLUE_4,
            'Purple' : PURPLE_4,
            'Pink'   : PINK_4,
        }
    },
    "Btn_Opt_Start_BG_Hover": {
        'Light': {
            'Default': GREY_9,
            'Red'    : RED_VIVID_5,
            'Orange' : ORANGE_VIVID_5,
            'Yellow' : YELLOW_VIVID_5,
            'Green'  : GREEN_VIVID_4,
            'Light Blue': BLUE_VIVID_6,
            'Blue'   : BLUE_VIVID_4,
            'Purple' : PURPLE_VIVID_4,
            'Pink'   : PINK_VIVID_7,
        },
        'Dark': {
            'Default': GREY_3,
            'Red'    : RED_5,
            'Orange' : ORANGE_5,
            'Yellow' : YELLOW_5,
            'Green'  : GREEN_5,
            'Light Blue': BLUE_8,
            'Blue'   : BLUE_5,
            'Purple' : PURPLE_5,
            'Pink'   : PINK_5,
        }
    },
    "Btn_Opt_Disabled": {
        'Light': {
            'Default': GREY_0,
            'Red'    : RED_VIVID_0,
            'Orange' : ORANGE_VIVID_0,
            'Yellow' : YELLOW_VIVID_0,
            'Green'  : GREEN_VIVID_0,
            'Light Blue': BLUE_VIVID_0,
            'Blue'   : BLUE_VIVID_0,
            'Purple' : PURPLE_VIVID_0,
            'Pink'   : PINK_VIVID_0,
        },
        'Dark': {
            'Default': GREY_0,
            'Red'    : RED_0,
            'Orange' : ORANGE_0,
            'Yellow' : YELLOW_0,
            'Green'  : GREEN_0,
            'Light Blue': BLUE_0,
            'Blue'   : BLUE_0,
            'Purple' : PURPLE_0,
            'Pink'   : PINK_0,
        }
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

            return res or ""

if __name__ == "__main__":
    print(ThemeManager.get('Base_BG_Color', 'Light', None))
