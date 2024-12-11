import tkinter as tk
import random

from game import Game

class PlatformerMenuApp:
    def __init__(self, master):
        self.master = master
        master.title("Onegai My Kuromi")
        master.geometry("800x600")
        master.configure(bg='black')

        # Create a canvas for background and animations
        self.canvas = tk.Canvas(master, width=800, height=600, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Title
        self.title_font = ("Press Start 2P", 48)
        self.canvas.create_text(400, 150, text="PIXEL QUEST",
                                font=self.title_font,
                                fill='#00FF00',
                                tags="title")

        # Subtitle
        self.subtitle_font = ("Press Start 2P", 16)
        self.canvas.create_text(400, 210, text="THE LOST KINGDOM",
                                font=self.subtitle_font,
                                fill='#00FFFF',
                                tags="subtitle")

        # Menu Buttons
        self.create_menu_buttons()

        # Pulsating title effect
        self.pulse_title()

    def create_menu_buttons(self):
        """Create interactive menu buttons"""
        button_font = ("Press Start 2P", 16)
        button_colors = {
            'normal': '#00FF00',
            'hover': '#00FFFF'
        }

        # Hover effect function
        def on_enter(e, button_id):
            self.canvas.itemconfig(button_id, fill=button_colors['hover'])

        def on_leave(e, button_id):
            self.canvas.itemconfig(button_id, fill=button_colors['normal'])

        # Start Game Button
        start_btn = self.canvas.create_text(
            400, 300,
            text="START GAME",
            font=button_font,
            fill=button_colors['normal'],
            tags="start_btn"
        )
        self.canvas.tag_bind(start_btn, '<Enter>', lambda e: on_enter(e, start_btn))
        self.canvas.tag_bind(start_btn, '<Leave>', lambda e: on_leave(e, start_btn))
        self.canvas.tag_bind(start_btn, '<Button-1>', self.start_game)

        # Options Button
        options_btn = self.canvas.create_text(
            400, 380,
            text="OPTIONS",
            font=button_font,
            fill=button_colors['normal'],
            tags="options_btn"
        )
        self.canvas.tag_bind(options_btn, '<Enter>', lambda e: on_enter(e, options_btn))
        self.canvas.tag_bind(options_btn, '<Leave>', lambda e: on_leave(e, options_btn))
        self.canvas.tag_bind(options_btn, '<Button-1>', self.show_options)

        # Quit Button
        quit_btn = self.canvas.create_text(
            400, 460,
            text="QUIT",
            font=button_font,
            fill=button_colors['normal'],
            tags="quit_btn"
        )
        self.canvas.tag_bind(quit_btn, '<Enter>', lambda e: on_enter(e, quit_btn))
        self.canvas.tag_bind(quit_btn, '<Leave>', lambda e: on_leave(e, quit_btn))
        self.canvas.tag_bind(quit_btn, '<Button-1>', self.quit_game)

    def pulse_title(self):
        """Create a pulsating effect for the title"""
        current_color = self.canvas.itemcget("title", "fill")
        new_color = '#00FFFF' if current_color == '#00FF00' else '#00FF00'
        self.canvas.itemconfig("title", fill=new_color)
        self.master.after(500, self.pulse_title)

    def start_game(self, event):
        """Placeholder for game start"""
        print("Starting game...")
        self.master.destroy()  # Explicitly close the menu window
        Game().run()

    def show_options(self, event):
        """Placeholder for options menu"""
        print("Opening options...")
        # Here you would typically open an options menu

    def quit_game(self, event):
        """Quit the game"""
        self.master.quit()

def main():
    root = tk.Tk()

    # Try to use a pixel font if available
    try:
        from tkinter import font
        custom_font = font.Font(family="Press Start 2P")
    except:
        print("Custom font not found. Using default.")

    app = PlatformerMenuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()