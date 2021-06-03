import tkinter as Tk        # Бибиотека для оконного приложения
import tkinter.ttk as ttk   # Библиотека виджетов для окна

root = Tk.Tk()

style = ttk.Style(root)
style.configure('lefttab.TNotebook', tabposition='wn')
style.configure('TNotebook.Tab', padding=(20, 8, 20, 0))

photo = Tk.PhotoImage(file = 'home.png')

note = ttk.Notebook(root, style='lefttab.TNotebook')
frame = Tk.Frame(note, width=250, height=100)
frame_w = Tk.Frame(note, width=250, height=100)
note.add(frame, image=photo)
note.add(frame_w, text = 'HOME')
note.pack()

root.mainloop()