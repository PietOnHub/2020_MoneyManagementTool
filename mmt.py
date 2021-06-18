from appData.calculator import calculate
from appData.categorizer import categorize
from appData.parser import parse
from appData.setup import setup
from appData.gui import mmtGui
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sys
import os
import json
import sqlite3
sys.dont_write_bytecode = True


def main():

    version = "0.1.0"
    author = "Piet"
    banner_gui = "Money.Management.Tool {} by {}".format(version, author)
    banner_cmd = "\n=========================== Money.Management.Tool {} by {} ============================".format(version, author)

    args = {}
    args["import_files"] = [["YOUR_FILE.csv", "YOUR_BANK", "Giro", "master"],["YOUR_FILE.csv", "YOUR_BANK", "Visa", "slave"]]
    args["import_dir"] = os.path.join(os.getcwd(), "import_private")
    args["config_dir"] = os.path.join(os.getcwd(), "config")
    args["bank_file"] = "bank.json"
    args["filter_file"] = "filter.json"
    args["interactive"] = True
    args["db_persistent"] = False
    args["gui"] = False

    db = DB
    session = Session

    print(banner_cmd)

    try:
        if args["db_persistent"]:
            if os.path.exists("data.db"):
                os.remove("data.db")
            db.connection = sqlite3.connect("data.db")
        else:
            db.connection = sqlite3.connect(":memory:")
        db.cursor = db.connection.cursor()
        print("\n> database connection established [ok]")
    except:
        print("\n> database connection could not get established [error]")
        sys.exit(1)

    if args["gui"]:
        print("\n> starting gui..")
        run_in_gui(args, session, db, banner_gui)
    else:
        run_in_shell(args, session, db, banner_cmd)


def run_in_gui(args, session, db, banner):

    root = tk.Tk()
    mmtGui(args, session, db, banner, root)
    tk.mainloop()
    close(db)


def run_in_shell(args, session, db, banner_cmd):

    setup(args, session)
    parse(args, session, db)
    categorize(args, session, db)
    calculate(args, session, db)

    while args["interactive"]:

        print("(1) recategorize or (2) exit ?")

        choice = input(" > ")
        if choice == "1":
            categorize(args, session, db)
        elif choice == "2":
            break
        else:
            print("unknown choice...")
            pass
    close(db)


class DB():
    pass


class Session():
    status = {
        "setup": False,
        "parser": False,
        "categorizer": False,
        "calculator": False
    }
    job_list = []
    balance = 0


def close(db):
    db.connection.commit()
    db.connection.close()
    print("\n> database connection closed [ok]")
    print("\nGoodbye!")
    sys.exit(0)


if __name__ == "__main__":
    main()
