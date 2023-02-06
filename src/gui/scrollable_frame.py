from gui.widgets import Scrollbar, Frame
import tkinter as tk


class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar = Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.scrollableFrame = Frame(self.canvas)

        self.scrollableFrame.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollableFrame, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # X11
        self.canvas.bind_all("<Button-4>", self.scroll_canvas)
        self.canvas.bind_all("<Button-5>", self.scroll_canvas)
        # everything else
        self.canvas.bind_all("<MouseWheel>", self.scroll_canvas)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def scroll_canvas(self, event):
        if event.num == 5 or event.delta < 0:
            direction = 1
        elif event.num == 4 or event.delta > 0:
            direction = -1

        self.canvas.yview_scroll(direction, "units")
