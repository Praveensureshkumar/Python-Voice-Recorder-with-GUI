import tkinter as tk
from tkinter import filedialog, messagebox
import sounddevice as sd

class AdvancedVoiceRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Voice Recorder")
        self.is_recording = False
        self.recording_data = []
        self.fs = 44100  # Sample rate
        self.tempfile = None
        self.recording_time = 0
        self.timer_thread = None
