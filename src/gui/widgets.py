import tkinter as tk
from config import config

BG = config.BG
BTTN_ACTIVE_BG = config.BTTN_ACTIVE_BG
DLT_BTTN_BG = config.DLT_BTTN_BG
DLT_BTTN_ACTIVE_BG = config.DLT_BTTN_ACTIVE_BG
BTTN_ACTIVE_FG = config.BTTN_ACTIVE_FG
BTTN_BG = config.BTTN_BG
BTTN_FG = config.BTTN_FG
BTTN_FONT = config.BTTN_FONT
BTTN_FONT_SIZE = config.BTTN_FONT_SIZE
BTTN_RELIEF = config.BTTN_RELIEF
ENTRY_BG = config.ENTRY_BG
ENTRY_FG = config.ENTRY_FG
ENTRY_RELIEF = config.ENTRY_RELIEF
FG = config.FG
FONT = config.FONT


class Frame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, bg=BG, **kwargs)


class LabelFrame(tk.LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, bg=BG, fg=FG, font=FONT, **kwargs)


class Label(tk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, bg=BG, fg=FG, font=FONT, **kwargs)


class Scrollbar(tk.Scrollbar):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            bd=0,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            activebackground=ENTRY_BG,
            **kwargs
        )


class Checkbutton(tk.Checkbutton):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            bg=BG,
            fg=ENTRY_FG,
            relief=ENTRY_RELIEF,
            selectcolor=ENTRY_BG,
            **kwargs
        )


class Entry(tk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            font=FONT,
            readonlybackground=ENTRY_BG,
            relief=ENTRY_RELIEF,
            bg=ENTRY_BG,
            fg=ENTRY_FG,
            **kwargs
        )


class Button(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            activebackground=BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=BTTN_BG,
            fg=BTTN_FG,
            **kwargs
        )


class DeleteButton(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            activebackground=DLT_BTTN_ACTIVE_BG,
            activeforeground=BTTN_ACTIVE_FG,
            relief=BTTN_RELIEF,
            font=(BTTN_FONT, BTTN_FONT_SIZE),
            bg=DLT_BTTN_BG,
            fg=BTTN_FG,
            **kwargs
        )
