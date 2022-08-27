import os
import multiprocessing as mp
import stat
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import time
from playsound import playsound
from gtts import gTTS
import pygame

import PyPDF2
import pyttsx3
from PIL import Image, ImageTk

cwd = os.getcwd()
speaker = pyttsx3.init()
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.master = master
        self.grid()

        self.numPages = None
        self.pagenum = 0
        self.fileisopen = False
        self.speakon = False

        self.draw_frames()
        self.draw_control_frames()
        # self.draw_display_frames()

        self.master.bind('<Left>', self.prevpage)
        self.master.bind('<Right>', self.nextpage)
        self.master.bind('<Up>', self.prevpage)
        self.master.bind('<Down>', self.nextpage)

    def draw_frames(self):
        # self.display_frame = tk.Frame(self, width=500, height=570, bg='#ab3a24')
        # self.display_frame.grid(row=0, column=0)
        # self.display_frame.grid_propagate(False)

        self.control_frame = tk.Frame(self, width=500, height=80, bg='#330b61')
        self.control_frame.grid(row=1, column=0)
        self.control_frame.grid_propagate(False)

    def draw_display_frames(self):
        pass
        # self.scrolly = tk.Scrollbar(self.display_frame, orient=tk.VERTICAL)
        # self.scrolly.grid(row=0, column=1, sticky='NS')

    def draw_control_frames(self):
        self.upload_btn = ttk.Button(self.control_frame, text="Upload", width=10, command=lambda: self.openfile())
        self.upload_btn.grid(row=0, column=0, padx=50, pady=10)

        self.previous_btn = ttk.Button(self.control_frame, image=previous_icon, width=10, command=lambda: self.prevpage)
        self.previous_btn.grid(row=0, column=3, padx=10, pady=10)

        self.pagevar = tk.StringVar()
        self.entry = ttk.Entry(self.control_frame, textvariable=self.pagevar, width=4, show=0)
        self.entry.grid(row=0, column=2, padx=10, pady=10)

        self.next_btn = ttk.Button(self.control_frame, image=next_icon, width=10,command=lambda: self.nextpage )
        self.next_btn.grid(row=0, column=1, padx=10, pady=10)

        self.speaker_btn = ttk.Button(self.control_frame, image=speakon_icon, width=10, command=self.speaker_toggle)
        self.speaker_btn.grid(row=0, column=4, padx=10, pady=10)

    def openfile(self):
        tempath = filedialog.askopenfilename(initialdir=cwd, filetypes=(("PDF", "*.pdf"),))
        if tempath:
            self.path = tempath
            self.f = open(self.path, "rb")
            self.pdf = PyPDF2.PdfFileReader(self.f)
            self.readpdf()


    def readpdf(self):

        self.readpage = self.pdf.pages[self.pagenum]
        self.text = self.readpage.extractText()
        myobj = gTTS(text=self.text, lang='en', slow=False)
        myobj.save("teset.mp3")
        song = "teset.mp3"
        # speaker.save_to_file(self.text, 'test.mp3')
        # speaker.runAndWait()
        if self.pagenum <= self.pdf.numPages:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            self.fileisopen = True
            thread = threading.Thread(target=self.play, daemon= True)
            # thread = threading.Thread(target=self.speak, args=(self.text,), daemon = True)
            thread.start()

        else:
            self.fileisopen = False
        while True:
            if self.checkNext():
                print("Goes to next")
                time.sleep(1)
                self.nextpage()
            else:
                print("pygame player is busy / version issue")
                self.checkNext()
    def checkNext(self):
        time.sleep(1)
        if pygame.mixer.music.get_busy():
            return True

    def play(self):
        song = 'teset.mp3'
        pygame.mixer.music.load(song)
        pygame.mixer.music.play(loops=0)
        while pygame.mixer.music.get_busy():
            time.sleep(2)

    def speak(self, text):
        if self.fileisopen:
            print(text)
            speaker.say(text)
            speaker.runAndWait()

    def nextpage(self, event=None):

        time.sleep(1)
        pygame.mixer.music.unload()
        time.sleep(2.5)
        # if speaker.isBusy():
        #     speaker.stop()
        print(self.pagenum)
        self.pagenum = self.pagenum + 1
        if self.pagenum < self.pdf.numPages:
            print(self.pdf.numPages)
            self.readpdf()

    def prevpage(self, event=None):
        speaker.stop()
        self.pagenum = self.pagenum - 1
        self.readpdf()

    def seek(self):
        if self.fileisopen:
            page = self.pagevar.get()
            if page != ' ':
                page = int(self.pagevar.get())
                if 0 < page < self.numPages + 1:
                    if page == 0:
                        page = 1
                    else:
                        page -= 1

                    self.pagenum = page
                    if speaker.isBusy():
                        speaker.endLoop()

                    self.pagevar.set('')
    def speaker_toggle(self, event=None):
        if not self.speakon:
            self.speakon = True
            self.speaker_btn['image'] = speakon_icon
            if self.fileisopen:
                self.speak()
        else:
            self.speakon = False
            self.speaker_btn['image'] = speakoff_icon
            if speaker._inLoop:
                speaker.endLoop()

def load_image(imge):
    img = Image.open(imge)
    icon = img.resize((32, 32))

    return icon


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('500x80+400+170')
    root.title('PDF AudioBook')
    root.resizable(0, 0)
    pygame.mixer.init()


    next_icon = ImageTk.PhotoImage(load_image(imge='venv/audio_icons/next.png'))
    previous_icon = ImageTk.PhotoImage(load_image(imge='venv/audio_icons/previous.png'))
    speakon_icon = ImageTk.PhotoImage(load_image(imge='venv/audio_icons/speaker.png'))
    speakoff_icon = ImageTk.PhotoImage(load_image(imge='venv/audio_icons/speakoff.png'))

    app = Application(master=root)
    app.mainloop()
