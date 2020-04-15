import tkinter as tk


def pushed(b):
    b["text"] = "After"


root = tk.Tk()  # make window
root.title("GUI using Tkinter")  # set titlef
root.geometry("320x240")  # size of win

label = tk.Label(root, text="Test Label")
label.grid()  # show the label

button = tk.Button(root, text="Before", command=lambda: pushed(button))  # make button
button.grid()

root.mainloop()
