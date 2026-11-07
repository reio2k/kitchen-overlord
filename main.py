import time
import tkinter as tk
import itertools
import threading
import requests
import json
import calendar
from customtkinter import *
from PIL import Image, ImageTk
from datetime import date
import p_names

from tkinter import font
from typing import List, Iterable, NamedTuple, Tuple, Dict

# --
# HELPER FUNCTIONS
# --



WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 600

START = date(2026,10,20) # day I start running the program.
today = date.today()

# images = {
#      "pmd": Image.open("path_to_your_image.jpg")
# }

def configure_grid_frame(
        frame: tk.Frame | tk.Tk,
        col_w: List[int], #column weights
        row_w: List[int], #row weights
        uniform_cols: bool = True,
        uniform_rows: bool = True,
        **kw
):
    col_group = "col" if uniform_cols else ""
    row_group = "row" if uniform_rows else ""
    
    num_col = len(col_w)
    num_row = len(row_w)

    for cw in range(num_col):
        frame.grid_columnconfigure(cw,weight=(col_w[cw]),uniform=col_group,**kw)
    for rw in range(num_row):
        frame.grid_rowconfigure(rw,weight=(row_w[rw]),uniform=row_group,**kw)

    
def writeCounter(
        self,
        row: int,
        frame
):

    necessity = self.necessities[row]
    self.nec_buttons[necessity][1] = False #writeCounter only gets called when someone finishes their job,
                                           #so in_works=False

    
    file = open("current_counters.txt", "r")
    file_lines = file.readlines()

    string_val, rest = file_lines[row].split(" ", 1)
    old_val = int(string_val)
    new_val = old_val+1

    file_lines[row] = str(new_val) + " " + rest

    self.nec_buttons[necessity][1] = False
    self.nec_labels[row].config(bg="#32a840",text=f"There's enough right now.")

    with open("current_counters.txt", "w") as file:
        file.writelines(file_lines)
    destroyFrame(self,frame)
    

def readCounter(
        row: int
) -> str:
    # row -= 1
    file = open("current_counters.txt", "r")
    for i in range(row):
        file.readline()
    person_value = file.readline().split()[0]
    return int(person_value)%4

def assignTask(self,row:int,frame):
    necessity = self.necessities[row]

    person_num = readCounter(row)
    person = people_names[person_num]
    self.nec_labels[row].config(text=f"TO BE DONE: {person}'s turn.",bg="#c42c43")
    self.nec_buttons[necessity][1] = True
    print(f"\n{self.nec_buttons} is the new nec_buttons")
    destroyFrame(self,frame)


def destroyFrame(self,frame):
            frame.destroy()
            self.activeFrame = None # so that new frames can be created by the necessity buttons


def create_button(
        curr_frame: tk.Frame | tk.Tk,
        text: str,
        font: Tuple,

        
):
    return

def read_address(
          
) -> Tuple[str,str]:
    file = open("postcode.txt","r")
    file_lines = file.readlines()
    postcode = str(file_lines[0]).removesuffix("\n")
    house_num = str(file_lines[1])
    types = ["residual_waste","gft","paper","pruning_waste","pmd","best_bag","christmas_trees","textile"]
    address_dict = {"postal_code":postcode,"house_number":house_num,"year":year,"types[]":types}

    return address_dict


def write_address(
    postcode: str,
    house_num: str
):
     new_txt = f"{postcode}\n{house_num}"

     with open("postcode.txt","w") as f:
          f.write(new_txt)
     


def scrape_afval(
          
):
     address_dict = read_address()
     r = requests.get("https://data.rd4.nl/api/v1/waste-calendar",params=address_dict)
     return r.json()

     
    

# --
# HELPER VARIABLES
# --

basic_string = "We have enough right now."

people_names = p_names.names
def next_three(items,today=None):
    today = date.today()
    total_list = []
    for item in items:
        if(len(total_list) >= 3): break
        i_date = date.fromisoformat(item["date"]) #the dates are in ISO format, so convert to date like so.
        if i_date >= today:
            total_list.append(item)
    while(len(total_list) < 3):
        total_list.append(None)
    return total_list
    

type_dict = {
    "pmd": ("PMD", Image.open("images\\pmd.png")),
    "residual_waste": ("general waste", Image.open("images\\general.png")),
    "textile": ("textile", Image.open("images\\textile.png")),
    "gft": ("organic waste", Image.open("images\\gft.png")),
    "paper": ("paper", Image.open("images\\paper.png")),
    "christmas_trees": ("christmas trees", Image.open("images\\christmas.png"))
}



def get_trash_dates(frame,labels):
    with open("afval_2026.json") as json_file:
        data = json.load(json_file)
        if(data["success"]):
            all_items = data["data"]["items"][0]
            three_list = next_three(all_items)
        else:
             three_list.append([None] * 3)

        for row,item in enumerate(three_list):
            i_date = date.fromisoformat(item["date"])
            i_type = type_dict[item["type"]][0]
            img_link = type_dict[item["type"]][1]
            curr_img = CTkImage(img_link,size=(40,40))

            day, m = (i_date).day, (i_date).month
            day_digits = list(map(int,str(day)))
            last_digit = day_digits[len(day_digits)-1]
            month = calendar.month_name[m]
            match last_digit:
                case 1:
                    suffix = "st"
                case 2:
                    suffix = "nd"
                case 3:
                    suffix = "rd"
                case _:
                    suffix = "th"
            msg = f"On the {day}{suffix} of {month}, {i_type} will be collected."
            labels[row].configure(text=msg,image=curr_img,compound="top")
        hour = 60*60*1000
        frame.after(hour,lambda:get_trash_dates(frame,labels))


def create_rounds(
          people,weeks_per_couple=2
        ):
    first, *others = people
    rounds = []
    for mate in others:
          pair = (first,mate)
          rest = tuple(p for p in people if p not in pair)
          rounds += [pair, rest] * (weeks_per_couple // 2) #if weeks_per_couple was 4, it'd add a round twice to rounds.
    return rounds

rounds = create_rounds(people_names)

def pair_for(day,rounds):
     week = (day - START).days //7 # integer difference in days divided by 7:
                           # week 0 = first week
     return rounds[week % len(rounds)] # 6 rounds, if week > 5,back to rounds[0]


class MainGUI():


    def __init__(self):

        # --
        # HELPER FUNCTIONS
        # --



        self.activeFrame = None # a placeholder which I set equal to a 'newFrame', which will prevent other buttons
        # from creating a newFrame, in case activeFrame is already pointing to something.

        # method and variables for assigning
        # recycling tasks

    

        def scheduleTrash(
                  label
        ):
            p1,p2 = pair_for(today,rounds)
            print(p1)
            label_text = f"{p1} and {p2} have to do recycling this weekend."
            label.configure(text=label_text)
            hour = 60*60*1000
            label.after(hour,lambda:scheduleTrash(self.trashLabel))
           
        

            

        # ROOT geometry

        self.root = tk.Tk()
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.title("B13 Kitchen Planner")

        self.root_col_weights = [2,5,1]
        self.root_row_weights = [1,1]

        configure_grid_frame(self.root,self.root_col_weights,self.root_row_weights)


        # ALL THE MAIN (ROOT) FRAMES

        self.calendarFrame = CTkFrame(self.root,fg_color="#338f52",border_color="black",border_width=4)
        self.calendarFrame.grid(row=0,column=0,rowspan=2,sticky="nsew")

        self.trashFrame = tk.Frame(self.root,bg="lightblue",relief="solid",borderwidth=3)
        self.trashFrame.grid(row=0,column=1,sticky="nsew")

        self.personFrame = tk.Frame(self.root,bg="black")
        self.personFrame.grid(row=0,column=2,sticky="nsew")

        self.necessityFrame = tk.Frame(self.root,bg="red")
        self.necessityFrame.grid(row=1,column=1,columnspan=2,sticky="nsew")

        # self.calendarFrame.grid_propagate(False)
        # self.trashFrame.grid_propagate(False)
        # self.personFrame.grid_propagate(False)
        self.necessityFrame.grid_propagate(False)

        # ------------------------------------------------------------

        # CALENDAR FRAME

        self.cal_col_weights = [1]
        self.cal_row_weights = [2,1,1]

        self.cal_labels = []
        configure_grid_frame(self.calendarFrame,
                            self.cal_col_weights,self.cal_row_weights,uniform_cols=False)


        for i in range(len(self.cal_row_weights)):
             cal_label = CTkLabel(self.calendarFrame,text="There are no other things to do",
                                  font=("Arial", 20),compound="right",text_color="black",
                                  border_color="black",border_width=2,corner_radius=2)
             cal_label.grid(row=i,column=0,sticky="nsew")
             self.calendarFrame.bind("<Configure>", lambda e,l=cal_label:l.configure(wraplength=e.width - 20))
             self.cal_labels.append(cal_label)

        
        self.items = []
        get_trash_dates(self.calendarFrame,self.cal_labels)

        



        # ------------------------------------------------------------

        # DISHES FRAME 'PERSON FRAME'

        self.person_col_weights = [1]
        self.person_row_weights = [1,1,1,1,1]
        configure_grid_frame(self.personFrame,self.person_col_weights,self.person_row_weights)

        # storing the person buttons that will be created
        # in a dict
        self.person_buttons = {}

        def dish_check(
                  person:str
        ):
            done_dishes = self.person_buttons[person][1]
            button = self.person_buttons[person][0]
            print(done_dishes)
            if(done_dishes):
                button.configure(image=dish_images["bad"],fg_color="orange")
                self.person_buttons[person][1] = False
            else:
                button.configure(image=dish_images["good"],fg_color="lightblue")
                self.person_buttons[person][1] = True
        
            

        dish_images = {
            "good": Image.open("images\\checkmark.png"),
            "bad": Image.open("images\\exclamation-mark.png")
        }

        for key,value in dish_images.items():
            dish_images[key] = CTkImage(value,size=(20,20))

        

        self.dish_label = CTkLabel(self.personFrame,text="DISHES",font=("Arial",20),
                                text_color="black",fg_color="#338f52",border_width=2,border_color="black")
        self.dish_label.grid(row=0,sticky="nsew")

        for row,person in enumerate(people_names):
            btn = CTkButton(self.personFrame,text=person,font=("Arial", 20),image=dish_images["good"],compound="right",
                        text_color="black",fg_color="lightblue",border_width=2,border_color="black",command=lambda p=person:dish_check(p))
            btn.grid(row=row+1,sticky="nsew")
            self.person_buttons[person] = [btn,True]
            print(self.person_buttons)

        # ------------------------------------------------------------

        # TRASH FRAME
        self.trash_row_weights = [2,3]
        configure_grid_frame(self.trashFrame,[1],self.trash_row_weights)

        recycling_todo_text = f"A and B have to do recycling this weekend."
        image = Image.open("images\\Recycle.png")
        image = image.resize((100,100))
        trash_image=ImageTk.PhotoImage(image)
        self.recycleLabel = CTkLabel(self.trashFrame,image=trash_image,text="",compound="bottom")
        self.recycleLabel.grid(row=0)

        self.trashLabel = CTkLabel(self.trashFrame, text=recycling_todo_text, anchor="n", font=("Arial", 28),border_width=2,fg_color="lightblue")
        self.trashLabel.grid(row=1)

        trash_width = self.trashFrame.winfo_width()
        print(f"THE RECYCLE LABEL WIDTH IS {trash_width}")
        self.trashLabel.configure(wraplength=trash_width - 20)

        self.trashFrame.bind("<Configure>", lambda e,l=self.trashLabel:l.configure(wraplength=e.width - 20))

        scheduleTrash(self.trashLabel)
        


        # NECESSITY FRAME

        self.nec_col_weights = [2,3]
        self.nec_row_weights = [1,1,1,1,1,1]
        configure_grid_frame(self.necessityFrame,
                             self.nec_col_weights,self.nec_row_weights)

        # BUTTONS WHEN THERE IS A NEED TO 
        # BUY NEW NECESSITIES

        def make_toggle(row:int, nec_name:str,frame):
            return lambda:use_toggle(row,nec_name,frame)

        def use_toggle(row,nec_name,frame):
            if self.activeFrame is not None:
                                        return # if activeFrame points
                                               # to something, then a newFrame is already created
            button_content = self.nec_buttons[nec_name]
            in_works = button_content[1] #T/F: bought/buy
            toggle(row,nec_name,in_works,frame)

        
        
        def toggle(given_row:int, necessity_name:str,in_works:bool,frame):

            self.newFrame = tk.Frame(frame)
            
            self.new_col_weights = [1,1]
            self.new_row_weights = [1,1]
            configure_grid_frame(self.newFrame,self.new_col_weights, self.new_row_weights)

            if in_works:
                p = readCounter(given_row)
                current_person = people_names[p]
                question_string = f"Did {current_person} buy {necessity_name}?"
            else:
                question_string = f"Do we need more {necessity_name}?"
            
            self.questionLabel = tk.Label(self.newFrame,text="", font=("Arial", 18),relief="solid",bg="lightblue")
            self.questionLabel.grid(row=0,column=0,columnspan=2,sticky="nsew")
            self.newFrame.bind("<Configure>",lambda e,q=self.questionLabel:q.configure(wraplength=e.width-20,text=question_string))

            lowercase_necessity = (necessity_name.split()[0]).lower() + "_todo"
            print(lowercase_necessity)

            current_frame = self.newFrame
            self.activeFrame = current_frame

            self.yesButton = tk.Button(self.newFrame, text="YES", font=("Arial", 18),relief="solid",bg="grey",
                                       command=lambda:writeCounter(self,given_row,current_frame) if in_works
                                       else assignTask(self,given_row,current_frame))
            self.yesButton.grid(row=1,column=0,sticky="nsew")

            self.noButton =tk.Button(self.newFrame, text="NO", font=("Arial", 18),relief="solid", bg="grey", command=lambda:destroyFrame(self,current_frame))
            self.noButton.grid(row=1,column=1,sticky="nsew")

            if (given_row>2):
                self.newFrame.grid(row=given_row-1,column=0,rowspan=2,sticky="nsew")
            else:
                self.newFrame.grid(row=given_row+1,column=0,rowspan=2,sticky="nsew")

            


        # ALL THE NECESSITY LABELS -------------------------------------------

        self.necessitiesLabel = CTkLabel(self.necessityFrame,text="Necessities",font=("Arial", 26), border_width=3,fg_color="white",border_color="black")
        self.necessitiesLabel.grid(row=0,column=0,columnspan=3,sticky="nsew")

        self.necessities = ["General Bags", "Soap", "Sponges", "Cloths", "Organic Bags"]
        buy_necessity = [False] * 5

        self.nec_buttons = {}
        self.nec_labels = []

        for row,necessity in enumerate(self.necessities):
            button = tk.Button(self.necessityFrame,text=necessity, font=("Arial", 18),
                                            anchor="w", borderwidth=2, relief="solid",
                                            command=make_toggle(row, necessity,self.necessityFrame))
            
            nec_basic_string = f"There's enough right now."
            label = tk.Label(self.necessityFrame,text=nec_basic_string,font=("Arial", 18),
                              borderwidth=2,relief="solid",bg="#32a840")
            
            
            button.grid(row=row+1,column=0,sticky="nsew")
            label.grid(row=row+1,column=1,sticky="nsew")
            self.nec_buttons[necessity] = [button,False]
            self.nec_labels.append(label)

        for necessity in self.nec_buttons:
             print(f"{necessity} is the necessity,{self.nec_buttons[necessity][1]} is the in_works value")

    
        # --------------------------------------------------------------------

        # TODO FRAME

        # self.todo_frame = tk.Frame(self.necessityLabel,bg="pink")
        # self.todo_frame.grid(row=1, column=1, rowspan=5, columnspan=2,sticky="nsew")

        general_todo = False
        soap_todo = False
        sponge_todo = False
        cloth_todo = False
        organic_todo = False




        self.root.mainloop()


MainGUI()

class ReceiptGUI():

    # you need to make sure that everything is static and never gets deleted.
    # Have some sort of text file where all the button presses get written to, all the undo's, etc.
    # and display it in this GUI whenever someone presses the receipt-gui-button.

    def __init__(self):
        pass



class PersonButton(tk.Button()):
    y_increment = 0
    # I am adding the pady_base and pady_step values into
    # the constructor, they need to be the same for every 
    # personButton. only the increment needs to change
    def __init__(self, master, pady_base=5,pady_step=2):

        defaults = {

        }
        pass

class CalendarGUI():
    def __init__(self):
        pass

class personGUI():
    def __init__(self,person,*args):
        self.person == person # Use this to create the specific person view, and its attributes
        pass
