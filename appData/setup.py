import os
import sys
import json


def setup(args, session):

    session.status["setup"] = False
    session.status["parser"] = False
    session.status["categorizer"] = False
    session.status["calculator"] = False

    print("\n> running setup:")
    print("- config path: {}".format(args["config_dir"]))
    print("- import path: {}".format(args["import_dir"]))

    bank_file_with_path = os.path.join(args["config_dir"], args["bank_file"])
    if os.path.exists(bank_file_with_path):
        print("- bank configuration: {} [ok]".format(args["bank_file"]))
        with open(bank_file_with_path) as bank_json:
            bank_list = json.load(bank_json)["bank"]
    else:
        print("Error - no config file for banks: {}".format(args["bank_file"]))
        if not args["gui"]:
            sys.exit(1)
        return(1)

    filter_file_with_path = os.path.join(args["config_dir"], args["filter_file"])
    if os.path.exists(filter_file_with_path):
        print("- filter configuration: {} [ok]".format(args["filter_file"]))
    else:
        print("- filter configuration: {} [not existing]".format(args["filter_file"]))

    job_count_total = len(args["import_files"])

    if job_count_total == 0:
        print("Error: no import files defined!")
        if not args["gui"]:
            sys.exit(1)
        return(1)

    job_count_current = 0
    job_list = []

    for current_job in args["import_files"]:

        job_count_current += 1
        job_complete = False
        job_file_name = current_job[0]
        job_bank_name = current_job[1]
        job_bank_type = current_job[2]
        job_dependency = current_job[3]

        if os.path.exists(os.path.join(args["import_dir"], job_file_name)):
            for bank in bank_list:
                if bank["name"] == job_bank_name and bank["type"] == job_bank_type:
                    print("- job {}/{}: {} [ok]".format(job_count_current, job_count_total, job_file_name))
                    job = {
                        "name": job_file_name,
                        "bank": bank["name"],
                        "type": bank["type"],
                        "structure": bank["structure"],
                        "formater": bank["formater"],
                        "dependency": job_dependency,
                        "balance": False,
                        "status": "complete",
                    }
                    job_list.append(job)
                    job_complete = True
                    break
            if not job_complete:
                print("- job {}/{}: {} [incomplete]".format(job_count_current, job_count_total, job_file_name))
        else:
            print("- job {}/{}: {} [not existing]".format(job_count_current, job_count_total, job_file_name))

    if len(job_list) > 0:
        print("> continuing with {} of {} jobs.".format(len(job_list), len(args["import_files"])))
        session.job_list = job_list
        session.bank_list = bank_list
        session.status["setup"] = True
        return(0)
    else:
        print("Error: no completely described job!")
        session.status["setup"] = False
        if not args["gui"]:
            sys.exit(1)
        return(1)
