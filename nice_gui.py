#!/usr/bin/env python

from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

import json
import os
import threading

import get_answers
import game
from client_bot import ClientBot

class Main(object):
    colours = ["#FFFFFF","#FF0000","#0000FF"]
    def __init__(self):
        self.root = Tk()
        self.load_answers()
        self.add_widgets()
        self.root.mainloop()
        
    def add_widgets(self):
        self.root.title("It's Life, Jim")
        
        self.root_menu = Menu(self.root)
        self.menu_file = Menu(self.root_menu, tearoff=0)
        self.menu_file.add_command(label="Add manual answer", command=self.add_answer)
        self.menu_file.add_command(label="Exit", command=self.root.quit)

        self.root_menu.add_cascade(label="File", menu=self.menu_file)
        self.root_menu.add_command(label="Run", command=self.start)
        self.root_menu.add_command(label="Pull Answers", command=self.pull_answers)
        self.root.config(menu=self.root_menu)
        self.add_root_widgets()
        
    def add_root_widgets(self):
        self.root_frame = Frame(self.root, height=315,width=455)
        self.root_frame.pack()
        self.listbox_frame = Frame(self.root_frame)
        self.listbox_frame.pack()
        self.list_1 = self.create_listbox(1)
        self.list_2 = self.create_listbox(2)
        self.canvas = Canvas(self.root_frame,
                             height=game.Game.y_size,
                             width=game.Game.x_size)
        self.image = PhotoImage(height=game.Game.y_size,
                                width=game.Game.x_size)
        self.canvas.create_image(0, 0, image = self.image, anchor=NW)
        self.canvas.pack()
    
    def create_listbox(self, lid, override = False):
        if not override:
            names, root = [answer[3] for answer in self.answers], self.listbox_frame
        else:
            names, root = override
        bot_listbox = Listbox(root, height=len(names), exportselection=0)
        for name in names:
            bot_listbox.insert(END, name)
        bot_listbox.grid(row=1,column=lid)
        return bot_listbox
        
    def load_answers(self):
        f = open("answers.json")
        self.answers = json.load(f)
        f.close()
    
    def pull_answers(self):
        msg = """This will disconnect all manual answers from the controller
                 They will have to be readded in order to select them"""
        if messagebox.askokcancel("Pull Answers?", msg):
            self.answers = get_answers.pull()
            self.root_frame.destroy()
            self.add_root_widgets()
    
    def add_answer(self):
        
        full_path = filedialog.askopenfilename()
        
        top = Toplevel(self.root)
        lb = self.create_listbox(1, [list(get_answers.languages.keys()),
                                     top])
        lb.bind('<<ListboxSelect>>', lambda evt: self.confirm_language(evt, top, full_path))
        
    def confirm_language(self, evt, top, full_path):
        w = evt.widget
        index = int(w.curselection()[0])
        language = w.get(index)
        top.destroy()
        filename, file_extension = os.path.splitext(os.path.basename(full_path))
        answer = ['sh', "'./commands/%s.sh'"%language, full_path, filename]
        get_answers.add_one(answer)
        self.answers.append(answer)
        
        self.root_frame.destroy()
        self.add_root_widgets()

    def start(self):
        index = int(self.list_1.curselection()[0])
        bot_1 = self.list_1.get(index)
        index = int(self.list_2.curselection()[0])
        bot_2 = self.list_2.get(index)
        bot_1 = ClientBot([answer for answer in self.answers if answer[3]==bot_1][0])
        bot_2 = ClientBot([answer for answer in self.answers if answer[3]==bot_2][0])
        new_event = threading.Event()
        self.game = game.Game(bot_1, bot_2, new_event)
        self.game.setup()
        self.image.blank()
        self.root.after(0, self.tick)
        
    def tick(self):
        for pos, owner in self.game.tick().items():
            if pos[0]<0 or pos[1]<0: continue
            self.image.put(Main.colours[owner], pos)
        print("Tick", self.game.tick_id)
        if self.game.tick_id == game.Game.no_generations:
            print("End game")
        else:
            self.root.after(10, self.tick)
        

def main():
        gui = Main()

if __name__ == '__main__':
        main()
        