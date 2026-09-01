import pygame
import numpy as np
import time


class TonePlayer:
  
    def __init__(self):
      
        pygame.mixer.init(frequency=44100, size=-16, channels=2)  

        self.sample_rate = 44100

       
        self.frequencies = {
            1: 523.25,    # C5
            2: 659.25,    # E5
            3: 783.99,    # G5
            4: 880.00,    # A5
            5: 1046.50,   # C6
            6: 1174.66,   # D6
            7: 1318.51,   # E6
            8: 1567.98,   # G6
            9: 1760.00,   # A6
            10: 1975.53   # B6
        }
        self.exit_frequency = 330.0

    def generate_tone(self, frequency, duration=0.20):
       
        samples = int(self.sample_rate * duration)

        t = np.linspace(0, duration, samples, False)

        # Generate sine wave
        wave = np.sin(2 * np.pi * frequency * t)

        # Fade in/out to avoid clicking sound
        fade_length = int(samples * 0.05)

        wave[:fade_length] *= np.linspace(0, 1, fade_length)
        wave[-fade_length:] *= np.linspace(1, 0, fade_length)

        # Convert to audio format (16-bit signed)
        mono_audio = np.int16(wave * 32767 * 0.4)
        stereo_audio = np.column_stack((mono_audio, mono_audio))  
        return pygame.sndarray.make_sound(stereo_audio)

    def _play_sequence(self, frequency, count):
        for _ in range(max(0, count)):
            self.generate_tone(frequency, duration=0.18).play()
            time.sleep(0.2)

    def play_entry_tone(self, occupancy_count):
        """Play one bright beep per person currently in the frame."""
        count = min(max(occupancy_count, 0), 10)
        if count:
            self._play_sequence(self.frequencies[count], count)

    def play_exit_tone(self, exit_count):
        """Play one lower exit beep for every person who left."""
        self._play_sequence(self.exit_frequency, min(max(exit_count, 0), 10))
    
    def play_for_count(self, count):
      
        if count <= 0:
            return

        # Cap at maximum tone
        if count > 10:
            count = 10

        # Get frequency for this count
        frequency = self.frequencies[count]

        # Generate and play tone
        sound = self.generate_tone(frequency)
        sound.play()