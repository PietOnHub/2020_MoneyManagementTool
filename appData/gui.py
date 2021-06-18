from appData.setup import setup
from appData.parser import parse
from appData.calculator import calculate
from appData.categorizer import categorize

import tkinter as tk


class mmtGui:

    def __init__(self, args, session, db, banner, root):

        self.root = root
        self.root.title(banner)

        self.header_frame_attributes = {"row": 0, "column": 0}
        self.content_frame_attributes = {"row": 1, "column": 0}

        content_list = ["setup", "process", "categorize", "analyze", "export"]

        self.header_frame = tk.Frame(master=root).grid(self.header_frame_attributes)

        self.content_frame = {}
        for item in content_list:
            self.content_frame[item] = tk.Frame(master=root)

        self.content_frame_current = self.content_frame["setup"]
        self.content_frame_current.grid(self.content_frame_attributes)

        def callback_click_button(arg):
            def _callback():
                return self.click_button(arg)
            return _callback

        self.header = {}
        for idx, item in enumerate(content_list):
            self.header[item] = tk.Button(
                master=self.header_frame,
                height=2, width=15,
                command=callback_click_button(item),
                text=item.title())
            self.header[item].grid(row=0, column=idx)

        self.content = {}
        self.create_view_setup(args, session)
        self.create_view_process(args, session, db)
        self.create_view_categorize(args, session, db)
        self.create_view_calculate(args, session, db)

    def click_button(self, new_content):

        print("\n> switching to", new_content)
        self.content_frame_current.grid_remove()
        self.content_frame[new_content].grid(self.content_frame_attributes)
        self.content_frame_current = self.content_frame[new_content]

    def create_view_setup(self, args, session):

        self.content["setup"] = tk.Button(
            master=self.content_frame["setup"],
            height=2, width=15,
            text="Load Setup",
            command=lambda: setup(args, session))
        self.content["setup"].grid(row=1, column=0)

    def create_view_process(self, args, session, db):

        self.content["process"] = tk.Button(
            master=self.content_frame["process"],
            height=2, width=15,
            text="Process Content",
            command=lambda: parse(args, session, db))
        self.content["process"].grid(row=0, column=0)

    def create_view_categorize(self, args, session, db):

        self.content["categorize"] = tk.Button(
            master=self.content_frame["categorize"],
            height=2, width=15,
            text="Categorize Content",
            command=lambda: categorize(args, session, db))
        self.content["categorize"].grid(row=0, column=0)

    def create_view_calculate(self, args, session, db):

        self.content["analyze"] = tk.Button(
            master=self.content_frame["analyze"],
            height=2, width=15,
            text="Analyze Content",
            command=lambda: calculate(args, session, db))
        self.content["analyze"].grid(row=0, column=0)
