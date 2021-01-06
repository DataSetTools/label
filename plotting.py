# PlottingProgram101.py
try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk


class FunctionFrame(object):
    def __init__(self, root):
        self._root = root
        functionRow = tk.Frame(root, relief='sunken')
        functionRow.grid(column=0, row=2)
        g1 = tk.Label(functionRow, text='Function in X: ')
        g1.pack(side='left')
        functionInXInput = tk.Entry(functionRow, width=35)
        functionInXInput.pack(side='left')
        h1 = tk.Label(functionRow, text='       Function Colour: ')
        h1.pack(side='left')
        functionColourInput = tk.Entry(functionRow, width=20)
        functionColourInput.pack(side='left')
        space = tk.Label(functionRow, text='       ')
        space.pack(side='left')
        b1 = tk.Button(functionRow, text='Select', padx=5,
                       command=createFunction())
        b1.pack(side='right')


class PlotFrame(object):
    def __init__(self, root):
        self._root = root
        plotRow = tk.Frame(root, relief='sunken')
        plotRow.grid(column=0, row=3, pady=20)
        a = tk.Label(plotRow, text='Plot Settings   ')
        a.pack(side='left')
        b1 = tk.Label(plotRow, text='Start X: ')
        b1.pack(side='left')
        startXInput = tk.Entry(plotRow, width=10)
        startXInput.pack(side='left')
        c1 = tk.Label(plotRow, text='   End X: ')
        c1.pack(side='left')
        endXInput = tk.Entry(plotRow, width=10)
        endXInput.pack(side='left')
        d1 = tk.Label(plotRow, text='  Start Y: ')
        d1.pack(side='left')
        startYInput = tk.Entry(plotRow, width=10)
        startYInput.pack(side='left')
        e1 = tk.Label(plotRow, text='   End Y: ')
        e1.pack(side='left')
        endYInput = tk.Entry(plotRow, width=10)
        endYInput.pack(side='left')
        f1 = tk.Label(plotRow, text='   Steps: ')
        f1.pack(side='left')
        stepsInput = tk.Entry(plotRow, width=10)
        stepsInput.pack(side='left')


class PlotApp(object):
    def __init__(self, root):
        self._root = root
        PlotFrame(root)
        FunctionFrame(root)
        self.createCanvas()

    def createCanvas(self):
        canvas = tk.Canvas(self._root, bg='white')
        canvas.grid(column=0, row=1, sticky='nwes')
        canvas.bind("<Button-1>", self.clicked)
        canvas.bind("<Enter>", self.moved)

    def clicked(self, event):
        x, y = event.x, event.y
        s = "Last point clicked at x=%s  y=%s" % (x, y)
        self._root.title(s)

    def moved(self, event):
        x, y = event.x, event.y
        s = "Cursor at x=%s  y=%s" % (x, y)
        self._root.title(s)


def createFunction():
    pass


def main():
    root = tk.Tk()
    app = PlotApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()