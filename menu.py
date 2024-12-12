import pygame
import sys

class Menu:
    def __init__(self, game):
        """
        Initialize the menu system

        :param game: The main Game instance to access assets, screen, etc.
        """
        self.game = game

        # Menu states
        self.STATE_MAIN_MENU = 0
        self.STATE_OPTIONS = 1
        self.STATE_CREDITS = 2

        # Current menu state
        self.current_state = self.STATE_MAIN_MENU

        # Menu options
        self.main_menu_options = [
            'Start Game',
            'Options',
            'Credits',
            'Quit'
        ]

        # Options menu items
        self.options_menu_options = [
            'Music Volume',
            'SFX Volume',
            'Back'
        ]

        # Selected option index
        self.selected_option = 0

        # Font setup
        self.font = pygame.font.Font(None, 36)
        self.selected_font = pygame.font.Font(None, 42)

        # Colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (150, 150, 150)
        self.BLACK = (0, 0, 0)

        # Music and SFX volumes
        self.music_volume = 0.5
        self.sfx_volume = 0.5

    def handle_events(self):
        """
        Handle menu navigation and selection events
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Navigation
                if event.key == pygame.K_UP:
                    self.selected_option = max(0, self.selected_option - 1)
                elif event.key == pygame.K_DOWN:
                    if self.current_state == self.STATE_MAIN_MENU:
                        self.selected_option = min(len(self.main_menu_options) - 1, self.selected_option + 1)
                    elif self.current_state == self.STATE_OPTIONS:
                        self.selected_option = min(len(self.options_menu_options) - 1, self.selected_option + 1)

                # Selection
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.select_option()

                # Volume adjustment in options
                if self.current_state == self.STATE_OPTIONS:
                    if event.key == pygame.K_LEFT:
                        if self.selected_option == 0:
                            self.music_volume = max(0, self.music_volume - 0.1)
                            pygame.mixer.music.set_volume(self.music_volume)
                        elif self.selected_option == 1:
                            self.sfx_volume = max(0, self.sfx_volume - 0.1)
                            # Adjust SFX volume for all sounds
                            for sfx in self.game.sfx.values():
                                sfx.set_volume(self.sfx_volume)

                    if event.key == pygame.K_RIGHT:
                        if self.selected_option == 0:
                            self.music_volume = min(1, self.music_volume + 0.1)
                            pygame.mixer.music.set_volume(self.music_volume)
                        elif self.selected_option == 1:
                            self.sfx_volume = min(1, self.sfx_volume + 0.1)
                            # Adjust SFX volume for all sounds
                            for sfx in self.game.sfx.values():
                                sfx.set_volume(self.sfx_volume)

                # Back option
                if event.key == pygame.K_ESCAPE:
                    if self.current_state != self.STATE_MAIN_MENU:
                        self.current_state = self.STATE_MAIN_MENU
                        self.selected_option = 0

    def select_option(self):
        """
        Handle menu option selection based on current state
        """
        if self.current_state == self.STATE_MAIN_MENU:
            if self.main_menu_options[self.selected_option] == 'Start Game':
                return 'start_game'
            elif self.main_menu_options[self.selected_option] == 'Options':
                self.current_state = self.STATE_OPTIONS
                self.selected_option = 0
            elif self.main_menu_options[self.selected_option] == 'Credits':
                self.current_state = self.STATE_CREDITS
                self.selected_option = 0
            elif self.main_menu_options[self.selected_option] == 'Quit':
                pygame.quit()
                sys.exit()

        elif self.current_state == self.STATE_OPTIONS:
            if self.options_menu_options[self.selected_option] == 'Back':
                self.current_state = self.STATE_MAIN_MENU
                self.selected_option = 0

    def render(self, display):
        """
        Render the current menu state

        :param display: Pygame surface to render menu on
        """
        # Fill background with a semi-transparent overlay
        overlay = pygame.Surface(display.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        display.blit(overlay, (0, 0))

        # Render based on current state
        if self.current_state == self.STATE_MAIN_MENU:
            self._render_menu(display, self.main_menu_options)

        elif self.current_state == self.STATE_OPTIONS:
            self._render_options(display)

        elif self.current_state == self.STATE_CREDITS:
            self._render_credits(display)

    def _render_menu(self, display, options):
        """
        Render the main menu or submenu

        :param display: Pygame surface to render on
        :param options: List of menu options to render
        """
        screen_width, screen_height = display.get_size()

        for i, option in enumerate(options):
            # Determine if this option is selected
            if i == self.selected_option:
                text = self.selected_font.render(option, True, self.WHITE)
                text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 50))
            else:
                text = self.font.render(option, True, self.GRAY)
                text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 50))

            display.blit(text, text_rect)

    def _render_options(self, display):
        """
        Render the options menu with volume controls

        :param display: Pygame surface to render on
        """
        screen_width, screen_height = display.get_size()

        # Render options with volume sliders
        options = [
            f'Music Volume: {"█" * int(self.music_volume * 10)}',
            f'SFX Volume:   {"█" * int(self.sfx_volume * 10)}',
            'Back'
        ]

        for i, option in enumerate(options):
            # Determine if this option is selected
            if i == self.selected_option:
                text = self.selected_font.render(option, True, self.WHITE)
                text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 50))
            else:
                text = self.font.render(option, True, self.GRAY)
                text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 50))

            display.blit(text, text_rect)

    def _render_credits(self, display):
        """
        Render the credits screen

        :param display: Pygame surface to render on
        """
        screen_width, screen_height = display.get_size()

        credits = [
            'Onegai My Kuromi',
            '',
            'Created by:',
            'Game Developer',
            '',
            'Special Thanks:',
            'Playtesters',
            'Family & Friends',
            '',
            'Press ESC to return'
        ]

        for i, line in enumerate(credits):
            text = self.font.render(line, True, self.WHITE)
            text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 30 - len(credits) * 15))
            display.blit(text, text_rect)