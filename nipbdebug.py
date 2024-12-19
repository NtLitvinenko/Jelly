import re
import tkinter as tk
from tkinter import Button, Label
from tkinter import messagebox
from decoder import parse_nip_markup as mpars
from JellyErrors import *
from os import getcwd
import traceback

class NIPBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Jelly! [Dev-#UNIC0002]")
        self.root.geometry("640x480")
        print(getcwd())
        markup = open("D:/dev/PKM/src/dbg/index.nmf", "r")
        widgets = mpars(markup.read())
        print(widgets)
        markup.close()
        self.make(widgets)

    widgets = {}
    styles = {}
    functions = {}

    def updatestyle(self, widget, style: dict):
        for param in style:
            if param == "x" or param == "y":
                self.widgets[widget].destroy()
                self.widgets[widget].pack(x=style["x"], y=style["y"])
            widget[param] = style[param]

    def make(self, string):
        try:
            for obj in string['styles']:
                self.styles[obj] = string['styles'][obj]
            for obj in string['labels']:
                print(obj, string['labels'][obj])
                self.createWidget("label", obj, self.styles[string['labels'][obj]["style"]])    
            for obj in string['buttons']:
                if re.search(r'\.onclick$', obj):
                    continue
                print(obj, string['buttons'][obj])
                self.createWidget("button", obj, self.styles[string['buttons'][obj]["style"]],
                                  onclick=string['buttons'][obj]['onclick'])

            # Store functions for later execution
            self.functions = string['functions']
        except Exception as e:
            self.errorHandler(e)

    def errorHandler(self, e: Exception):
        messagebox.showerror(f"Error caught!!!", str(e))
        traceback.print_exc()

    def createWidget(self, type, name, style, **kwargs):
        if type == "label":
            # Must be text, x, y
            self.widgets[name] = Label(self.root, text=style['text'])
            self.widgets[name].place(x=int(style['x']), y=int(style['y']))
        elif type == "button":
            # Must be text, x, y
            self.widgets[name] = Button(self.root, text=style['text'])
            self.widgets[name].place(x=int(style['x']), y=int(style['y']))

            # Check for 'onclick' in kwargs
            if 'onclick' in kwargs:
                # Handle the onclick event
                self.widgets[name]["command"] = lambda: self.handle_onclick(kwargs['onclick'])

    def handle_onclick(self, onclick):
        # Check if the onclick is a function
        print(f"OnClick worked!: {onclick}")
        if onclick in self.functions:
            self.execute_function(onclick)

    def execute_function(self, function_name):
        if function_name in self.functions:
            commands = self.functions[function_name]['commands']
            for command in commands:
                command = command.strip()
                if command.startswith("exec:"):
                    exec_command = command[5:].strip()
                    self.execute_exec_command(exec_command)
                else:
                    # Handle other commands (like updating styles)
                    if '=' in command:
                        target, style_name = command.split('=')
                        target = target.strip()
                        style_name = style_name.strip()
                        if target in self.widgets and style_name in self.styles:
                            self.updatestyle(self.widgets[target], self.styles[style_name])

    def execute_exec_command(self, exec_command):
        try:
            alt = re.split(r'\?(?![^\[]*\])', exec_command)

            # Replace '[?]' with '?' in the parts
            alt = [i.replace("[?]", "?") for i in alt]
        except Exception as e:
            self.errorHandler(e)
            return

        cmd = alt[0]
        try:
            if cmd == "print":
                print(alt[1])
            elif cmd == "destroy":
                widget_name = alt[1]
                if widget_name in self.widgets:
                    self.widgets[widget_name].destroy()
                    self.widgets.pop(widget_name)
            elif cmd == "createWidget":
                type = alt[1].split("_")[0]
                print(type)
                if type != "button":
                    self.createWidget(type, alt[1], self.styles[alt[2]])
                elif type == "button":
                    print(self.styles[alt[2]])
                    self.createWidget(type, alt[1], self.styles[alt[2]], onclick=alt[3])
            else:
                raise UnknownElementException(f"Catched error at \"exec\", Lexed String: {alt}")
        except Exception as e:
            self.errorHandler(e)


if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = NIPBrowser(root)  # Create an instance of the NIPBrowser class
    root.mainloop()  # Start the Tkinter event loop