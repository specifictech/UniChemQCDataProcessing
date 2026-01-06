from tkinter import Tk

from classes.ui import UI

def main():
    root = Tk()
    app = UI(root)
    root.mainloop()

if __name__ == "__main__":
    main()