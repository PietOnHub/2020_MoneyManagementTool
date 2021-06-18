import os
import sys
import json


def categorize(args, session, db):

    if session.status["parser"] == False:
        print("Error: Please process data first!")
        if not args["gui"]:
            sys.exit(1)
        return(1)

    session.status["categorizer"] = False

    print("\n> categorizing data:")

    db.cursor.execute("SELECT Count() FROM buchung")
    count_found = 0
    count_total = db.cursor.fetchone()[0]

    filter_file = args["filter_file"]
    filter_file_with_path = os.path.join(args["config_dir"], filter_file)
    if os.path.exists(filter_file_with_path):
        print("- loading filter file!")
        with open(filter_file_with_path) as filter_json:
            filter_groups = json.load(filter_json)["filter_groups"]
    else:
        print("Error - no config file for filter: {}".format(filter_file))
        if not args["gui"]:
            sys.exit(1)
        return(1)

    updated_list = []

    query = "SELECT Id, Buchungstext, Gegenkonto, Verwendungsnachweis, Beschreibung FROM buchung"
    data = db.cursor.execute(query)
    headers = [i[0] for i in db.cursor.description]

    for data_row in data:

        found = 0
        effective_filter = []
        current_id = data_row[0]

        for filter_group in filter_groups:
            for filter_definition in filter_group["definitions"]:

                found_in_this_group = False

                if filter_definition["field"] == []:
                    check_list = ["Buchungstext", "Gegenkonto", "Verwendungsnachweis", "Beschreibung"]
                else:
                    check_list = filter_definition["field"]

                for field in check_list:
                    if filter_definition["phrase"].upper() in data_row[headers.index(field)].upper():

                        effective_filter.append("{}:{}".format(filter_group["name"], filter_definition["phrase"]))
                        current_category = filter_group["name"]
                        found_in_this_group = True
                        found += 1
                        break

                if found_in_this_group:
                    break

            if found > 1:
                print("WARNING - filter matching in multiple categories: \n - transaction: {} \n - filter: {}".format(data_row, effective_filter))
                break

        if found == 1:
            updated_list.append((current_category, current_id))
            count_found += 1

    db.cursor.executemany("UPDATE buchung set kategorie = ? WHERE id = ?", updated_list)

    quota = count_found / count_total * 100
    print("- quota: {:0.1f}% - {} of {} transactions are categorized!".format(quota, count_found, count_total))

    session.status["categorizer"] = True

    query = """SELECT Kategorie, Betrag, Buchungstext, Gegenkonto, REPLACE(Verwendungsnachweis, '  ', ''), Beschreibung FROM buchung 
        WHERE Datum BETWEEN date('now','-1 months') AND date('now','0 months') 
        ORDER BY Kategorie"""
    data = db.cursor.execute(query)

    for data_row in data:
        print(data_row)


    return 0
