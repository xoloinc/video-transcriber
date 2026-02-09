"""
Video till Undertexter - Transkriberar video med OpenAI Whisper API
Dra och släpp en videofil för att generera SRT-undertexter.
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import tempfile
import os
from pathlib import Path
from datetime import timedelta

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

def _find_ffmpeg():
    """Hittar ffmpeg - antingen inbyggd bredvid exe:n eller i systemet."""
    # Om vi kör som PyInstaller-bundle, leta bredvid exe:n
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
        for name in ('ffmpeg', 'ffmpeg.exe'):
            p = bundle_dir / name
            if p.exists():
                return str(p)
    # Fallback: imageio-ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    # Fallback: system ffmpeg
    return "ffmpeg"

FFMPEG_PATH = _find_ffmpeg()

# Inbyggd API-nyckel (injiceras vid bygge via GitHub Actions)
BUILTIN_API_KEY = "__OPENAI_API_KEY__"


class VideoTranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video till Undertexter")
        self.root.geometry("500x400")
        self.root.configure(bg="#2b2b2b")

        self.has_builtin_key = BUILTIN_API_KEY and not BUILTIN_API_KEY.startswith("__")
        self.api_key = tk.StringVar(value=BUILTIN_API_KEY if self.has_builtin_key else "")
        self.status_var = tk.StringVar(value="Dra och släpp en videofil här")
        self.progress_var = tk.DoubleVar(value=0)

        self.setup_ui()
        self.setup_drag_drop()

    def setup_ui(self):
        # Visa API-nyckel-fältet bara om ingen nyckel är inbyggd
        if not self.has_builtin_key:
            api_frame = ttk.Frame(self.root, padding=10)
            api_frame.pack(fill="x")
            ttk.Label(api_frame, text="OpenAI API-nyckel:").pack(anchor="w")
            api_entry = ttk.Entry(api_frame, textvariable=self.api_key, show="*", width=50)
            api_entry.pack(fill="x", pady=5)

        # Drop-zon
        self.drop_frame = tk.Frame(
            self.root,
            bg="#3c3c3c",
            highlightbackground="#5c5c5c",
            highlightthickness=2,
            cursor="hand2"
        )
        self.drop_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="Dra och släpp videofil här\neller klicka för att välja",
            font=("Segoe UI", 14),
            fg="#cccccc",
            bg="#3c3c3c",
            pady=50
        )
        self.drop_label.pack(expand=True)

        # Klickbar drop-zon
        self.drop_frame.bind("<Button-1>", self.browse_file)
        self.drop_label.bind("<Button-1>", self.browse_file)

        # Status och progress
        status_frame = ttk.Frame(self.root, padding=10)
        status_frame.pack(fill="x")

        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 10)
        )
        self.status_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            mode="determinate",
            length=400
        )
        self.progress_bar.pack(fill="x", pady=5)

    def setup_drag_drop(self):
        """Försöker konfigurera drag-and-drop med tkinterdnd2 om tillgängligt."""
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD

            # Om vi använder TkinterDnD root
            if hasattr(self.root, 'drop_target_register'):
                self.drop_frame.drop_target_register(DND_FILES)
                self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)
                self.drop_label.config(text="Dra och släpp videofil här\neller klicka för att välja")
        except ImportError:
            # tkinterdnd2 inte installerat - använd bara klick
            self.drop_label.config(text="Klicka här för att välja videofil\n(installera tkinterdnd2 för drag-and-drop)")

    def handle_drop(self, event):
        """Hanterar när en fil släpps."""
        file_path = event.data
        # Rensa bort klamrar om de finns (Windows)
        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]
        self.process_video(file_path)

    def browse_file(self, event=None):
        """Öppnar filväljare för video."""
        file_path = filedialog.askopenfilename(
            title="Välj videofil",
            filetypes=[
                ("Videofiler", "*.mp4 *.mkv *.avi *.mov *.webm *.wmv *.flv"),
                ("Alla filer", "*.*")
            ]
        )
        if file_path:
            self.process_video(file_path)

    def process_video(self, video_path):
        """Startar transkribering i bakgrundstråd."""
        if not self.api_key.get().strip():
            messagebox.showerror("Fel", "Ange din OpenAI API-nyckel först!")
            return

        if OpenAI is None:
            messagebox.showerror(
                "Fel",
                "OpenAI-biblioteket är inte installerat.\n"
                "Kör: pip install openai"
            )
            return

        # Kör i bakgrundstråd för att inte frysa GUI
        thread = threading.Thread(
            target=self.transcribe_video,
            args=(video_path,),
            daemon=True
        )
        thread.start()

    def update_status(self, message, progress=None):
        """Uppdaterar status-text och progress bar."""
        self.status_var.set(message)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()

    def transcribe_video(self, video_path):
        """Huvudfunktion för transkribering."""
        try:
            video_path = Path(video_path)

            if not video_path.exists():
                raise FileNotFoundError(f"Filen hittades inte: {video_path}")

            self.update_status(f"Bearbetar: {video_path.name}", 10)

            # Steg 1: Extrahera ljud
            self.update_status("Extraherar ljud från video...", 20)
            audio_path = self.extract_audio(video_path)

            # Steg 2: Transkribera med Whisper
            self.update_status("Transkriberar med Whisper API...", 40)
            segments = self.transcribe_audio(audio_path)

            # Steg 3: Skapa SRT-fil
            self.update_status("Skapar undertextfil...", 80)
            srt_path = video_path.with_suffix(".srt")
            self.create_srt(segments, srt_path)

            # Städa upp temp-fil
            if audio_path.exists():
                os.remove(audio_path)

            self.update_status(f"Klart! Sparad: {srt_path.name}", 100)

            # Visa meddelande
            self.root.after(0, lambda: messagebox.showinfo(
                "Klart!",
                f"Undertexter sparade till:\n{srt_path}"
            ))

        except Exception as e:
            self.update_status(f"Fel: {str(e)}", 0)
            self.root.after(0, lambda: messagebox.showerror("Fel", str(e)))

    def extract_audio(self, video_path):
        """Extraherar ljud från video med ffmpeg."""
        # Skapa temp-fil för ljud
        temp_dir = tempfile.gettempdir()
        audio_path = Path(temp_dir) / f"{video_path.stem}_audio.mp3"

        # ffmpeg kommando (använder inbyggd ffmpeg)
        cmd = [
            FFMPEG_PATH, "-y",  # Overwrite output
            "-i", str(video_path),
            "-vn",  # Ingen video
            "-acodec", "libmp3lame",
            "-ar", "16000",  # 16kHz sample rate (bra för Whisper)
            "-ac", "1",  # Mono
            "-q:a", "4",  # Kvalitet
            str(audio_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg fel: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg hittades inte!\n"
                "Installera paketet: pip install imageio-ffmpeg"
            )

        return audio_path

    def transcribe_audio(self, audio_path):
        """Transkriberar ljud med OpenAI Whisper API (ord-nivå precision)."""
        client = OpenAI(api_key=self.api_key.get().strip())

        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

        return self.group_words_to_segments(response.words)

    def group_words_to_segments(self, words, max_words=10, max_duration=5.0):
        """Grupperar ord till undertextsegment med exakta timestamps."""
        segments = []
        current_words = []
        segment_start = None

        for word in words:
            if segment_start is None:
                segment_start = word.start

            current_words.append(word.word.strip())
            duration = word.end - segment_start

            if len(current_words) >= max_words or duration >= max_duration:
                segments.append({
                    "start": segment_start,
                    "end": word.end,
                    "text": " ".join(current_words)
                })
                current_words = []
                segment_start = None

        # Sista segmentet
        if current_words:
            segments.append({
                "start": segment_start,
                "end": words[-1].end,
                "text": " ".join(current_words)
            })

        return segments

    def format_timestamp(self, seconds):
        """Konverterar sekunder till SRT-timestamp format (HH:MM:SS,mmm)."""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def create_srt(self, segments, output_path):
        """Skapar SRT-fil från transkriberade segment."""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, 1):
                start = self.format_timestamp(segment["start"])
                end = self.format_timestamp(segment["end"])
                text = segment["text"].strip()

                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")


def main():
    # Försök använda TkinterDnD för drag-and-drop
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()

    # Tema
    style = ttk.Style()
    style.theme_use("clam")

    app = VideoTranscriberApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
