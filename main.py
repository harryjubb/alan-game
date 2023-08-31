# Imports
import time
import random
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from pngdec import PNG

# Setup
display = PicoGraphics(display=DISPLAY_TUFTY_2040)

# PNG renderer
# Use as a global and load files in each time, or else we hit memory issues
png = PNG(display)

# Buttons
button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_c = Button(9, invert=False)
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)

all_buttons = [
    button_a,
    button_b,
    button_c,
    button_up,
    button_down
]

display.set_backlight(1.0)

# Constants
WIDTH, HEIGHT = display.get_bounds()
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
SKY_BLUE = display.create_pen(0, 127, 255)

# Functions and classes
def title_screen():
    display.set_pen(BLACK)
    display.clear()

    display.set_pen(WHITE)
    display.text("The Alan Game!", 20, 100, 320, 4)
    display.text(f"Press B to start", 20, 200, 320, 2)
    display.update()

    time.sleep(3)
    
def game_over_screen(score):
    display.set_pen(BLACK)
    display.clear()

    display.set_pen(WHITE)
    display.text("Game Over!", 20, 100, 320, 4)
    display.text(f"Score: {score}", 20, 150, 320, 4)
    display.text(f"Press B to try again", 20, 200, 320, 2)
    display.update()

def check_collision(a, b):
    return a.x + a.width >= b.x and a.x <= b.x + b.width and a.y + a.height >= b.y and a.y <= b.y + b.height

class Cloud():
    
    def __init__(self, initial_x, initial_y, initial_speed=5):
        self.x = initial_x
        self.y = initial_y
        self.speed = initial_speed
    
    def render(self):
        display.set_pen(WHITE)
        display.circle(self.x, self.y, 12)
        display.circle(self.x + 15, self.y, 10)
        display.circle(self.x + 7, self.y - 10, 10)
        
class Alan():
    
    def __init__(self, initial_x, initial_y, initial_speed=15):
        self.x = initial_x
        self.y = initial_y
        self.speed = initial_speed
        
        png.open_file("adoranheadsmall.png")
        self.width = png.get_width()
        self.height = png.get_height()
        
    def move_up(self):
        self.y = max(self.y - self.speed, 0)
        
    def move_down(self):
        self.y = min(self.y + self.speed, HEIGHT - self.height)
    
    def render(self):
        png.open_file("adoranheadsmall.png")
        png.decode(self.x, self.y)

class Present():
    
    def __init__(self, initial_x, initial_y, initial_speed=10):
        self.x = initial_x
        self.y = initial_y
        self.speed = initial_speed
        
        png.open_file("present.png")
        self.width = png.get_width()
        self.height = png.get_height()
    
    def render(self):
        png.open_file("present.png")
        png.decode(self.x, self.y)
        
class Stone():
    
    def __init__(self, initial_x, initial_y, initial_speed=10):
        self.x = initial_x
        self.y = initial_y
        self.speed = initial_speed
        
        png.open_file("stone2.png")
        self.width = png.get_width()
        self.height = png.get_height()
    
    def render(self):
        png.open_file("stone2.png")
        png.decode(self.x, self.y)
    

class Game():
    
    def __init__(self):
        #self.reset()
        pass
        
    def reset(self):
        self.score = 0
        self.hearts = 3
        self.ended = False
        
        self.alan = Alan(20, 120)
        
        self.clouds = [
            Cloud(random.randint(0, WIDTH + 200), random.randint(0, HEIGHT))
            for i in range(6)
        ]
        
        self.presents = [
            Present(random.randint(WIDTH, WIDTH + 200), random.randint(0, HEIGHT))
            for i in range(3)
        ]

        self.stones = [
            Stone(random.randint(WIDTH, WIDTH + 200), random.randint(0, HEIGHT))
            for i in range(3)
        ]

        # Initial render
        self.render()
        
    @property
    def objs(self):
        return self.clouds + self.presents + self.stones
    
    def render(self):
        # Render sky
        display.set_pen(SKY_BLUE)
        display.clear()
        
        # Render clouds
        for obj in self.objs:
            obj.render()
            
        # Render alan
        self.alan.render()
        
        # Render hearts
        png.open_file("heart.png")
        for i in range(3):
            pos = (WIDTH - (png.get_width() * (i + 1)), 0)
                
            heart_file = "heart.png" if self.hearts > i else "heart_black.png"
                
            png.open_file(heart_file)
            png.decode(*pos)
        
        # Render score
        display.set_pen(WHITE)
        display.text(f"{self.score}", 0, 0, 320, 4)
        
        # Update display
        display.update()
        
        
    def tick(self):
        # Respond to button presses
        if button_up.read():
            self.alan.move_up()
        
        if button_down.read():
            self.alan.move_down()
        
        # Shift objects left        
        for obj in self.objs:
            obj.x = obj.x - obj.speed
        
        # Re-render
        self.render()
        
        # Detect collisions        
        for obj_list, obj_type in [(self.clouds, Cloud), (self.presents, Present), (self.stones, Stone)]:
            
            if obj_type is Present:
                for obj in obj_list:
                    if check_collision(self.alan, obj):
                        self.score += 1
                        obj_list.remove(obj)
            
            if obj_type is Stone:
                for obj in obj_list:
                     if check_collision(self.alan, obj):
                         self.hearts -= 1
                         obj_list.remove(obj)
            
            # Remove out-of-bounds objects
            for obj in obj_list:
                if obj.x < -50:
                    obj_list.remove(obj)
        
            # Create replacements for any missing objects
            while len(obj_list) < (6 if obj_type is Cloud else 3):
                obj_list.append(obj_type(random.randint(WIDTH, WIDTH + 200), random.randint(0, HEIGHT)))
                
        # Check for end of game
        if self.hearts == 0:
            game.ended = True
            self.render()
        

if __name__ == "__main__":
    title_screen()
    
    while not button_b.read():
        pass
    
    game = Game()
    
    while 1:
        
        game.reset()
        
        while not game.ended:
            game.tick()
            #time.sleep(0.0166)
        
        game_over_screen(game.score)
        
        while not button_b.read():
            pass
