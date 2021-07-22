import os
import sys
from datetime import datetime
import csv
import json
import re


def parse(args, session, db):

    if session.status["setup"] == False:
        print("Error: Please provide valid setup first!")
        if not args["gui"]:
            sys.exit(1)
        return(1)

    session.status["parser"] = False
    session.status["categorizer"] = False
    session.status["calculator"] = False

    print("\n> running parser:")

    job_count = 0
    transactions_count_total = 0
    session.balance = 0

    db.cursor.execute("""DROP TABLE IF EXISTS buchung""")
    db.cursor.execute("""CREATE TABLE buchung(
        Id INTEGER PRIMARY KEY autoincrement,
        Datum TEXT, 
        Betrag DECIMAL(10,2), 
        Buchungstext TEXT, 
        Gegenkonto TEXT, 
        Verwendungsnachweis TEXT,
        Beschreibung TEXT,
        Kategorie TEXT,
        Quelle TEXT)""")

    for job in session.job_list:

        transactions_count = 0
        job_count += 1
        time_range = []
        structure = job["structure"]
        formater = job["formater"]

        print("> processing {} of {} jobs:".format(job_count, len(session.job_list)))
        print("- file: {}".format(job["name"]))

        import_file_with_path = os.path.join(args["import_dir"], job["name"])

        try:
            with open(import_file_with_path, newline='') as csvfile:
                line_count = 0
                spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
                for current_line in spamreader:
                    line_count += 1

                    if line_count == structure["balance"][0]:
                        balance_raw = current_line[structure["balance"][1]]
                        if formater["saldo"]["thousand"] == ".":
                            balance_unified = balance_raw.replace(".", "")
                            balance_unified = balance_unified.replace(",", ".")
                        if formater["saldo"]["thousand"] == ",":
                            balance_unified = balance_raw.replace(",", "")
                        balance = str(re.findall(r"\-?\d*\.?\,?\d+", balance_unified)[0])
                        job["balance"] = float(balance)

                    if line_count > structure["header_line"]:

                        date_string_raw = current_line[structure["header_columns"]["Datum"]]
                        year = date_string_raw.split(".")[2]
                        month = date_string_raw.split(".")[1]
                        day = date_string_raw.split(".")[0]
                        datestring = "{}-{}-{}".format(year, month, day)

                        amount_raw = current_line[structure["header_columns"]["Betrag"]]
                        if formater["transaction"]["thousand"] == ".":
                            amount = amount_raw.replace(".", "")
                            amount = amount.replace(",", ".")
                        if formater["transaction"]["thousand"] == ",":
                            amount = amount_raw.replace(",", "")

                        def column_finder(line, structure, column_name):
                            if column_name in structure["header_columns"]:
                                return line[structure["header_columns"][column_name]]
                            else:
                                return "-/-"

                        db.cursor.execute("INSERT INTO buchung (Datum, Betrag, Buchungstext, Gegenkonto, Verwendungsnachweis, Beschreibung, Kategorie, Quelle) VALUES (?,?,?,?,?,?,?,?)", (
                            datestring, amount, column_finder(current_line, structure, "Buchungstext"),
                            column_finder(current_line, structure, "Gegenkonto"),
                            column_finder(current_line, structure, "Verwendungsnachweis"),
                            column_finder(current_line, structure, "Beschreibung"),
                            "Keine",
                            job["name"]
                        ))

                        transactions_count += 1

                        if datestring not in time_range:
                            time_range.append(datestring)

            transactions_count_total += transactions_count

            session.balance += job["balance"]

            print("- dependency: {}".format(job["dependency"]))
            print("- balance: {}".format(job["balance"]))
            print("- transactions: {}".format(transactions_count))
            print("- time range: {} to {}".format(min(time_range), max(time_range)))

        except:
            print("Warning: could not parse file [skipping]")

    if transactions_count_total > 0:
        last_date = datetime.strptime(max(time_range), '%Y-%m-%d')
        today = datetime.today()
        diff = today - last_date
        print("> total balance: {:.2f}".format(session.balance))
        print("> total transactions: {}. Last entry {} days ago.".format(transactions_count_total, diff.days))
        session.status["parser"] = True
        return(0)
    else:
        print("Error: no transactions found!")
        session.status["parser"] = False
        if not args["gui"]:
            sys.exit(1)
        return(1)
