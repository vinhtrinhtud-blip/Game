import math
import random
import time
import tkinter as tk


WIDTH = 800
HEIGHT = 500


class SpaceCatGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Mèo Vũ Trụ — Python")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg="#11183d",
            highlightthickness=0
        )
        self.canvas.pack()

        self.stars = [
            [random.randrange(WIDTH), random.randrange(HEIGHT),
             random.uniform(0.5, 1.8), random.uniform(10, 32)]
            for _ in range(85)
        ]
        self.keys = set()
        self.objects = []
        self.score = 0
        self.lives = 3
        self.player_x = WIDTH / 2
        self.target_x = self.player_x
        self.player_y = HEIGHT - 76
        self.spawn_timer = 0.3
        self.hit_flash = 0
        self.running = False
        self.last_time = time.monotonic()
        self.start_button = None

        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.canvas.bind("<Motion>", self.move_mouse)
        self.canvas.bind("<Button-1>", self.move_mouse)
        self.draw_scene()
        self.show_overlay(
            "Sẵn sàng cất cánh?",
            "Hứng cà phê để ghi điểm, né thiên thạch để giữ 3 mạng nhé!",
            "Bắt đầu chơi"
        )
        self.tick()

    def key_down(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == "space" and not self.running:
            self.start_game()

    def key_up(self, event):
        self.keys.discard(event.keysym.lower())

    def move_mouse(self, event):
        if self.running:
            self.target_x = event.x

    def show_overlay(self, title, message, button_text):
        self.canvas.delete("overlay")
        self.canvas.create_rectangle(
            0, 0, WIDTH, HEIGHT, fill="#0b1027", stipple="gray50",
            outline="", tags="overlay"
        )
        self.canvas.create_text(
            WIDTH / 2, 184, text="🐱", font=("Segoe UI Emoji", 38),
            fill="white", tags="overlay"
        )
        self.canvas.create_text(
            WIDTH / 2, 238, text=title, font=("Segoe UI", 25, "bold"),
            fill="#fff5d6", tags="overlay"
        )
        self.canvas.create_text(
            WIDTH / 2, 279, text=message, width=440,
            font=("Segoe UI", 13), fill="#dedaf5", tags="overlay"
        )
        self.start_button = tk.Button(
            self.root, text=button_text, command=self.start_game,
            font=("Segoe UI", 12, "bold"), bg="#ffd36e",
            fg="#18132e", activebackground="#ffbd78",
            relief="flat", padx=20, pady=8, cursor="hand2"
        )
        self.canvas.create_window(
            WIDTH / 2, 337, window=self.start_button, tags="overlay"
        )

    def start_game(self):
        if self.start_button is not None:
            self.start_button.destroy()
            self.start_button = None
        self.canvas.delete("overlay")
        self.score = 0
        self.lives = 3
        self.objects.clear()
        self.spawn_timer = 0.3
        self.hit_flash = 0
        self.player_x = self.target_x = WIDTH / 2
        self.running = True
        self.canvas.focus_set()

    def finish_game(self):
        self.running = False
        self.show_overlay(
            "Hết pin cà phê rồi!",
            f"Bạn ghi được {self.score} điểm. Thử thêm chuyến bay nữa nhé!",
            "Chơi lại"
        )

    def update(self, dt):
        direction = (
            int("right" in self.keys or "d" in self.keys)
            - int("left" in self.keys or "a" in self.keys)
        )
        if direction:
            self.target_x = self.player_x + direction * 360 * dt
        self.target_x = max(34, min(WIDTH - 34, self.target_x))
        self.player_x += (self.target_x - self.player_x) * min(1, dt * 13)

        self.spawn_timer += dt
        if self.spawn_timer >= max(0.38, 0.82 - self.score / 1200):
            kind = "coffee" if random.random() < 0.58 else "asteroid"
            self.objects.append({
                "type": kind,
                "x": random.uniform(35, WIDTH - 35),
                "y": -35,
                "speed": (150 if kind == "coffee" else 185)
                         + min(self.score * 1.3, 100),
                "radius": random.uniform(15, 21),
                "phase": random.random() * math.tau,
            })
            self.spawn_timer = 0

        remaining = []
        for obj in self.objects:
            obj["y"] += obj["speed"] * dt
            obj["phase"] += dt * (2 if obj["type"] == "coffee" else 1.5)
            dx = abs(obj["x"] - self.player_x)
            dy = abs(obj["y"] - self.player_y)
            limit = 28 if obj["type"] == "coffee" else obj["radius"] + 22
            if dx < limit and dy < limit:
                if obj["type"] == "coffee":
                    self.score += 10
                    continue
                if self.hit_flash <= 0:
                    self.lives -= 1
                    self.hit_flash = 1
                    if self.lives <= 0:
                        self.finish_game()
                        return
                    continue
            if obj["y"] < HEIGHT + 45:
                remaining.append(obj)
        self.objects = remaining
        self.hit_flash = max(0, self.hit_flash - dt)

        for star in self.stars:
            star[1] = (star[1] + star[3] * dt) % HEIGHT

    def draw_coffee(self, x, y, phase):
        x, y = int(x), int(y)
        sway = math.sin(phase) * 3
        self.canvas.create_line(x - 5, y - 20, x - 8, y - 27, fill="#fff0d5", width=2, tags="scene")
        self.canvas.create_line(x + 5, y - 20, x + 7, y - 28, fill="#fff0d5", width=2, tags="scene")
        self.canvas.create_oval(x - 13 + sway, y - 15, x + 13 + sway, y + 14, fill="#fff0d5", outline="#e5cda9", width=2, tags="scene")
        self.canvas.create_rectangle(x - 11 + sway, y - 10, x + 11 + sway, y - 3, fill="#8b503b", outline="", tags="scene")
        self.canvas.create_oval(x + 9 + sway, y - 7, x + 22 + sway, y + 6, outline="#fff0d5", width=3, tags="scene")

    def draw_asteroid(self, x, y, radius, phase):
        points = []
        for i in range(10):
            angle = i * math.tau / 10 + phase
            r = radius * (1 if i % 2 == 0 else 0.78)
            points.extend((x + math.cos(angle) * r, y + math.sin(angle) * r))
        self.canvas.create_polygon(
            points, fill="#ff7186", outline="#ffc0b8", width=2,
            smooth=True, tags="scene"
        )
        self.canvas.create_oval(x - 7, y - 4, x - 1, y + 2, fill="#cf526c", outline="", tags="scene")
        self.canvas.create_oval(x + 3, y + 3, x + 9, y + 9, fill="#cf526c", outline="", tags="scene")

    def draw_ship(self):
        x, y = self.player_x, self.player_y
        flame = random.randint(10, 20)
        self.canvas.create_polygon(
            x - 8, y + 25, x, y + 25 + flame, x + 8, y + 25,
            fill="#ff9f61", outline="", tags="scene"
        )
        self.canvas.create_polygon(
            x - 17, y + 5, x - 37, y + 22, x - 15, y + 23,
            fill="#67b8fa", outline="#e7f4ff", width=2, tags="scene"
        )
        self.canvas.create_polygon(
            x + 17, y + 5, x + 37, y + 22, x + 15, y + 23,
            fill="#67b8fa", outline="#e7f4ff", width=2, tags="scene"
        )
        self.canvas.create_polygon(
            x, y - 37, x + 22, y - 5, x + 17, y + 26,
            x - 17, y + 26, x - 22, y - 5,
            fill="#f5f6ff", outline="#566091", width=3, smooth=True, tags="scene"
        )
        self.canvas.create_oval(x - 14, y - 22, x + 14, y + 12, fill="#6573ba", outline="", tags="scene")
        self.canvas.create_oval(x - 10, y - 14, x + 10, y + 10, fill="#ffd19b", outline="", tags="scene")
        self.canvas.create_oval(x - 5, y - 7, x - 2, y - 2, fill="#202343", outline="", tags="scene")
        self.canvas.create_oval(x + 2, y - 7, x + 5, y - 2, fill="#202343", outline="", tags="scene")
        self.canvas.create_oval(x - 2, y + 1, x + 2, y + 4, fill="#f17c9b", outline="", tags="scene")

    def draw_scene(self):
        self.canvas.delete("scene")
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#11183d", outline="", tags="scene")
        self.canvas.create_oval(470, -90, 800, 240, fill="#211c4b", outline="", tags="scene")
        for x, y, size, _speed in self.stars:
            self.canvas.create_oval(x, y, x + size, y + size, fill="#e2e4ff", outline="", tags="scene")
        for obj in self.objects:
            if obj["type"] == "coffee":
                self.draw_coffee(obj["x"], obj["y"], obj["phase"])
            else:
                self.draw_asteroid(obj["x"], obj["y"], obj["radius"], obj["phase"])
        self.draw_ship()
        self.canvas.create_text(
            24, 28, anchor="w", text=f"ĐIỂM  {self.score}",
            font=("Segoe UI", 16, "bold"), fill="white", tags="scene"
        )
        hearts = "♥" * self.lives + "♡" * (3 - self.lives)
        self.canvas.create_text(
            WIDTH - 24, 28, anchor="e", text=f"MẠNG  {hearts}",
            font=("Segoe UI", 16, "bold"), fill="#ff9cae", tags="scene"
        )
        if self.hit_flash > 0:
            self.canvas.create_rectangle(
                0, 0, WIDTH, HEIGHT, fill="#ff4b6e",
                stipple="gray75", outline="", tags="scene"
            )

    def tick(self):
        now = time.monotonic()
        dt = min(now - self.last_time, 0.04)
        self.last_time = now
        if self.running:
            self.update(dt)
        self.draw_scene()
        self.root.after(16, self.tick)


def main():
    root = tk.Tk()
    SpaceCatGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
