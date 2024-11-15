import tkinter as tk
from tkinter import filedialog, messagebox
import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tempfile
import threading
import time
import os


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

        # GUI setup
        self.record_button = tk.Button(root, text="Record", command=self.start_recording)
        self.record_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", state=tk.DISABLED, command=self.stop_recording)
        self.stop_button.pack(pady=10)

        self.play_button = tk.Button(root, text="Play", state=tk.DISABLED, command=self.play_recording)
        self.play_button.pack(pady=10)

        self.save_button = tk.Button(root, text="Save", state=tk.DISABLED, command=self.save_recording)
        self.save_button.pack(pady=10)

        # Timer label
        self.timer_label = tk.Label(root, text="Recording Time: 0 s")
        self.timer_label.pack(pady=5)

        # Waveform display
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.recording_data = []
            self.tempfile = tempfile.mktemp(suffix=".wav")
            self.record_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.play_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)

            # Start the recording stream and timer thread
            sd.default.samplerate = self.fs
            sd.default.channels = 1
            self.recording_stream = sd.InputStream(callback=self.audio_callback)
            self.recording_stream.start()

            self.recording_time = 0
            self.timer_thread = threading.Thread(target=self.update_timer)
            self.timer_thread.start()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.recording_stream.stop()
            self.recording_stream.close()
            write(self.tempfile, self.fs, np.concatenate(self.recording_data, axis=0))
            self.record_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.play_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            messagebox.showinfo("Advanced Voice Recorder", "Recording saved to temporary file.")

    def play_recording(self):
        if self.tempfile and os.path.exists(self.tempfile):
            rate, data = read(self.tempfile)
            sd.play(data, rate)

    def save_recording(self):
        if self.tempfile and os.path.exists(self.tempfile):
            save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
            if save_path:
                os.rename(self.tempfile, save_path)
                messagebox.showinfo("Advanced Voice Recorder", f"Recording saved to {save_path}")

    def update_timer(self):
        while self.is_recording:
            time.sleep(1)
            self.recording_time += 1
            self.timer_label.config(text=f"Recording Time: {self.recording_time} s")

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.recording_data.append(indata.copy())
            self.update_waveform(indata)

    def update_waveform(self, audio_chunk):
        self.ax.clear()
        self.ax.plot(audio_chunk)
        self.ax.set_ylim([-1, 1])
        self.canvas.draw()


# Set up the main window
root = tk.Tk()
app = AdvancedVoiceRecorder(root)
root.mainloop()
