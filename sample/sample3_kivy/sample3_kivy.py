import os
import platform

if platform.system() == "windows":
    os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
    # os.environ ['KIVY_GL_BACKEND'] = 'angle_sdl2'

import kivy

kivy.require('1.7.2')

from kivy.app import App
from kivy.uix.button import Button


class TestApp(App):
    def build(self):
        return Button(text='Hello World')


def main():
    TestApp().run()


if __name__ == "__main__":
    main()
