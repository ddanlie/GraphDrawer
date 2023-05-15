import tkinter as tk
from tkinter import ttk
import random
import math


class LabelInput(ttk.Frame):
    def __init__(self, root, input_class, label_text, textvar=None, 
                    label_args=None, input_args=None, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
    
        self.textvar = textvar

        label_args = label_args or {}
        input_args = input_args or {}
        
        if input_class in (ttk.Checkbutton, ttk.Radiobutton, ttk.Button):
            input_args["text"] = label_text
            input_args["variable"] = self.textvar
        else:
            self.label = ttk.Label(self, text=label_text, **label_args)
            self.label.grid(row=0, column=0, sticky='WE')
            input_args["textvariable"] = self.textvar

        self.input = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky='WE')

        self.columnconfigure(0, weight=1)

    def get_input_object(self):
        return self.input

    def grid(self, sticky="WE", **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def get(self):
        if self.textvar != None:
            return self.textvar.get()
        elif type(self.input) == tk.Text:
            return self.input.get("1.0", tk.END)
        else:
            try:
                return self.input.get()
            except(TypeError):
                return ""

class ScrollableFrame(tk.Frame):

    def __init__(self, root, orient=tk.VERTICAL, canvas_columns=1,
                canvas_args=None, canvframe_args=None, sbar_args=None, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        canvas_args = canvas_args or {}
        canvframe_args = canvframe_args or {}
        sbar_args = sbar_args or {}
        
        self.canvas = tk.Canvas(self, **canvas_args, height=kwargs["height"])
        self.canvframe = tk.Frame(self.canvas, **canvframe_args)

        scommand: callable
        if orient == tk.VERTICAL:
            scommand = self.canvas.yview
        elif orient == tk.HORIZONTAL:
            scommand = self.canvas.xview
        
        self.scrollbar = tk.Scrollbar(self, command=scommand, **sbar_args)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.canvframe.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        canvframe_id = self.canvas.create_window((0,0), anchor='nw', window=self.canvframe)

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(
                canvframe_id, width=e.width
            )
        )

        self.canvas.grid(row=0, column=0)
        self.scrollbar.grid(row=0, column=1, sticky="SN")


    def get_container(self):
        return self.canvframe



class GraphNode():

    def __init__(self, canvas, size, num, coords:tuple):
        self.coords = coords
        self.num = num
        self.canvas = canvas
        self.size = size

    def draw_node(self):
        self.canvas.create_oval(self.coords[0]-self.size, self.coords[1]-self.size, 
                                self.coords[0]+self.size, self.coords[1]+self.size, fill='black')
    
    def draw_num(self):
        self.canvas.create_text(self.coords[0], self.coords[1], text=f"{self.num}", fill='white')


class NodeConnection():

    def __init__(self, canvas, g1:GraphNode, g2:GraphNode):
        self.c1 = g1.coords
        self.c2 = g2.coords
        self.canvas = canvas
    
    def draw(self):
        self.canvas.create_line(self.c1[0], self.c1[1], self.c2[0], self.c2[1], width=1, fill='black')


class GraphSettingsFrame(tk.Frame):
    
    
    def __init__(self, root, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.inputs = []
        self.rows = 3
        self.columns = 3
        self.inpidx = 0
        self.add_input_button = LabelInput(self, ttk.Button, "add", None, None, {"command":self.add_input})
        self.pop_input_button = LabelInput(self, ttk.Button, "remove", None, None, {"command":self.del_input})
        self.save_input_button = LabelInput(self, ttk.Button, "draw", None, None, {"command":self.draw_graph})
        self.title = ttk.Label(self, text="DRAW A GRAPH", font=("TkDefaultFont", 16))
        self.title.grid(row=0, column=0, columnspan=self.columns, pady=(50, 25))
        self.add_input_button.grid(row=1, column=0)
        self.pop_input_button.grid(row=1, column=1)
        self.save_input_button.grid(row=1, column=2)
        
        self.sframe = ScrollableFrame(self, height=kwargs["height"]//2)
        self.sframe.grid(row=2, column=0, columnspan=self.columns, pady=(25, 0))

        for i in range(self.columns):
            self.columnconfigure(i, weight=1)

    def add_input(self):
        self.inputs.append(LabelInput(self.sframe.get_container(), ttk.Entry, f"node {self.inpidx+1}"))
        self.inputs[self.inpidx].pack(fill=tk.X, padx=50)
        self.inpidx += 1


    def del_input(self):
        self.inpidx -= 1
        if self.inpidx < 0:
            self.inpidx = 0
            return
        self.inputs[self.inpidx].destroy()
        del self.inputs[self.inpidx]

    def draw_graph(self):
        self.data = [[0 for _ in range(len(self.inputs))] for _ in range(len(self.inputs))]
        for i, elem in enumerate(self.inputs):
            connected_nodes = []
            if elem.get() == "":
                connected_nodes = [i+1]
            else:
                connected_nodes = list(map(int, elem.get().split(" ")))
            for cn in connected_nodes:
                try:
                    self.data[i][cn-1] = 1
                except IndexError:
                    pass
        self.master.draw_graph()

class GraphFrame(tk.Frame):

    def __init__(self, root, n=10, adj_mat=None, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        adj_mat = adj_mat or [[1 for _ in range(n)] for _ in range(n)]
        self.canvas = tk.Canvas(self, height=kwargs["height"], width=kwargs["width"])

        if n <= 0:
            self.canvas.pack()
            return

        self.r = (min(kwargs["height"], kwargs["width"]) // 2) - \
                   (min(kwargs["height"], kwargs["width"]) // 4)
 
        self.nr = self.r // len(adj_mat)
        self.center = (kwargs["width"] // 2, kwargs["height"] // 2)
        self.alpha = -360 // len(adj_mat)
        self.alpha = (self.alpha/180) * math.pi + (((-360 % len(adj_mat)/len(adj_mat))/180) * math.pi)


        nodes = []
        coord_n = (0, self.r)
        for i in range(len(adj_mat)):
            nodes.append(GraphNode(self.canvas, self.nr, i+1,
                                (self.center[0]+coord_n[0], self.center[0]-coord_n[1])))
            coord_n = (coord_n[0] * math.cos(self.alpha) - coord_n[1] * math.sin(self.alpha), 
                        coord_n[0] * math.sin(self.alpha) + coord_n[1] * math.cos(self.alpha))
        
        connections = []
        nodes_to_draw = set()
        for i in range(len(adj_mat)):
            for j in range(len(adj_mat)):
                if bool(adj_mat[i][j]):
                    connections.append(NodeConnection(self.canvas, nodes[i], nodes[j]))
                    nodes_to_draw.add(nodes[i])
                    nodes_to_draw.add(nodes[j])


        for c in connections:
            c.draw()          
        for n in nodes_to_draw:
            n.draw_node()
            n.draw_num()
         
        self.canvas.pack()



class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("App")
        self.resizable(False, False)
        self.geometry("1000x500")

        mat = []
        n = 10
        for i in range(n):
            mat.append([not bool(random.randint(0,10)) for i in range(n)])

        self.sf = GraphSettingsFrame(self, height=500, width=400)
        self.sf.grid(row=0, column=0, sticky="SN")
        self.gf = GraphFrame(self, adj_mat=mat, height=500, width=600)
        self.gf.grid(row=0, column=1, sticky="SN")

    def draw_graph(self):
        self.gf.destroy()
        self.gf = GraphFrame(self, adj_mat=self.sf.data, height=500, width=600)
        self.gf.grid(row=0, column=1, sticky="SN")



root = MyApp()
root.mainloop()

