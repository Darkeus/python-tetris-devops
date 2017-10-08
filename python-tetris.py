import pyglet
import config
import map
import piece
from pyglet.gl import *


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.map = map.Map(int(self.width/config.UNIT),
                           int(self.height/config.UNIT))

    def on_draw(self):
        self.clear()
        self.map.render()

    def on_text_motion(self, motion):
        self.map.move(motion)

    def on_key_press(self, symbol, modifier):
        if symbol == pyglet.window.key.SPACE:
            self.map.hard_drop()
        elif symbol == pyglet.window.key.MOTION_UP:
            self.map.rotate_cw()
        elif symbol == pyglet.window.key.Z:
            self.map.rotate_ccw()

    def piece_gravity(self, dt):
        self.map.gravity()


if __name__ == '__main__':
    window = Window(400, 880,
                    "Python Tetris", resizable=True)
    pyglet.clock.schedule_interval(window.piece_gravity,
                                   config.GRAVITY_INTERVAL)
    pyglet.app.run()
