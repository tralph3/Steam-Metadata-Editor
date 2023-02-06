from tkinter import filedialog, messagebox


def ask_steam_path():
    messagebox.showinfo(
        title="Can't locate Steam",
        message="Steam couldn't be located in your system, "
        + "or there's no \"appinfo.vdf\" file present. "
        + "Please point to it's installation directory."
    )
    return filedialog.askdirectory()
