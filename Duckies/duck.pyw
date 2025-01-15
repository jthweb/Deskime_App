import tkinter as tk
import time
import random


class Duck:
    def __init__(self):
        self.window = tk.Tk()
        self.load_images()
        self.frame_index = 0
        self.img = self.move_left_images[self.frame_index]
        self.timestamp = time.time()
        self.last_direction_change = time.time()
        self.initialize_window()
        self.dir = -1
        self.move_pet()
        self.window.mainloop()

    def load_images(self):
        self.move_left_images = [tk.PhotoImage(file='duck-left.gif', format='gif -index %i' % i) for i in range(10)]
        self.move_right_images = [tk.PhotoImage(file='duck-right.gif', format='gif -index %i' % i) for i in range(10)]

    def initialize_window(self):
        self.window.config(background='black')
        self.window.wm_attributes('-transparentcolor', 'black')
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.label = tk.Label(self.window, bd=0, bg='black')
        self.x = 1040
        self.y = self.window.winfo_screenheight()-80
        self.label.configure(image=self.img)
        self.label.pack()
        self.window.geometry('128x128+{}+{}'.format(self.x, self.y))

    def change_frame(self, direction):
        if time.time() > self.timestamp + 0.05:
            self.timestamp = time.time()
            self.frame_index = (self.frame_index + 1) % 5
            self.img = direction[self.frame_index]

    def change_direction(self):
        # Generate a random number between 0 and 1
        random_number = random.random()

        if random_number < 0.5:
            self.dir = -self.dir  # Change direction randomly with a 50% chance

    def move_pet(self):
        if time.time() > self.last_direction_change + 10:
            self.last_direction_change = time.time()
            self.change_direction()

        self.x = self.x + self.dir

        if self.dir < 0:
            direction = self.move_left_images
        else:
            direction = self.move_right_images

        self.change_frame(direction)

        if self.x <= 0 or self.x >= (self.window.winfo_screenwidth() - 128):
            self.dir = -self.dir

        self.window.geometry('128x128+{}+{}'.format(self.x, self.y))
        self.label.configure(image=self.img)
        self.label.pack()
        self.window.after(10, self.move_pet)
        self.window.lift()


if __name__ == "__main__":
    Duck()
