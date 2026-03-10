import pygame


class AudioManager:
    def __init__(self, resource_path_func):
        self.muted = False
        self.enabled = True
        self.sounds = {}

        try:
            pygame.mixer.init()
            self.sounds = {
                'jump': pygame.mixer.Sound(resource_path_func('assets/sfx/jump.wav')),
                'coin': pygame.mixer.Sound(resource_path_func('assets/sfx/coin.wav')),
                'victory': pygame.mixer.Sound(resource_path_func('assets/sfx/victory.wav')),
                'game_over': pygame.mixer.Sound(resource_path_func('assets/sfx/game_over.wav')),
            }
        except Exception:
            self.enabled = False

    def toggle_mute(self):
        self.muted = not self.muted

    def play(self, name):
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
