"""---------------------------------------------------------------------------------------------------------------------
  File Name:   color.py
  End Result:  A class to store and format strings for RGBA colors
  Author:      Connor Cozad (23ccozad@gmail.com)
  Created:     August 14, 2020
---------------------------------------------------------------------------------------------------------------------"""

class Color:
    """Stores and formats strings for RGBA colors"""

    def __init__(self, red, green, blue, alpha='None'):
        """Create a new Color by providing red, green, and blue channels. Alpha (aka transparency) is optional."""
        self.set_red(red)
        self.set_green(green)
        self.set_blue(blue)
        self.set_alpha(alpha)

    def set_red(self, red):
        self.red = str(red)

    def set_green(self, green):
        self.green = str(green)

    def set_blue(self, blue):
        self.blue = str(blue)

    def set_alpha(self, alpha):
        self.alpha = str(alpha)

    def get_red(self):
        return self.red

    def get_green(self):
        return self.green

    def get_blue(self):
        return self.blue

    def get_alpha(self):
        return self.alpha

    def color_to_str(self, alpha='None'):
        """Print a string representation of the color. The alpha channel is optional."""
        if alpha != 'None':
            return 'rgba(' + self.get_red() + ', ' + self.get_green() + ', ' + self.get_blue() + ', ' + str(alpha) + ')'
        elif self.get_alpha() != 'None':
            return 'rgba(' + self.get_red() + ', ' + self.get_green() + ', ' + self.get_blue() + ', ' + self.get_alpha() + ')'
        else:
            return 'rgb(' + self.get_red() + ', ' + self.get_green() + ', ' + self.get_blue() + ')'

    def __str__(self):
        """Print a string representation of the color. The alpha channel is optional. This method is the same as
        color_to_str(), expect that color_to_str() allows an alpha channel to be provided at the time the method is
        called. If you want __str__() to produce a string with an alpha channel, it must be set in the object's
        attribute named 'alpha'"""
        if self.get_alpha() != 'None':
            return 'rgba(' + self.get_red() + ', ' + self.get_green() + ', ' + self.get_blue() + ', ' + self.get_alpha() + ')'
        else:
            return 'rgb(' + self.get_red() + ', ' + self.get_green() + ', ' + self.get_blue() + ')'