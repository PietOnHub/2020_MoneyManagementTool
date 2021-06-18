from datetime import datetime
import sqlite3, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def calculate(args, session, db):

    if session.status["parser"] == False:
        print("Error: Please process data first!")
        if not args["gui"]:
            sys.exit(1)
        return(1)

    session.status["calculator"] = False

    queryCatPerYear = ("SELECT strftime('%Y',datum) as Year, kategorie as Kategorie, round(SUM(betrag),2) as Betrag FROM buchung GROUP BY Year, kategorie")
    df_y = pd.read_sql_query(queryCatPerYear, db.connection)
    df_y_mod = df_y.pivot(index="Kategorie", columns="Year", values="Betrag").fillna(0)

    queryCatPerMon = ("SELECT strftime('%Y/%m',datum) as Month, kategorie as Kategorie, round(SUM(betrag),2) as Betrag FROM buchung GROUP BY Month, kategorie")
    df_m = pd.read_sql_query(queryCatPerMon, db.connection)
    df_m_mod = df_m.pivot(index="Month", columns="Kategorie", values="Betrag").fillna(0)

    # ------------------------------------------------------------------------------------------
    # CAT LAST YEAR (PIE)

    queryCatPerRange = """
        SELECT (?) as Zeitraum, kategorie as Kategorie, ABS(SUM(betrag)) as Total 
        FROM buchung 
        WHERE date(datum) BETWEEN date((?)) and date((?)) GROUP BY Kategorie"""
    df_Total = pd.read_sql(queryCatPerRange, db.connection, params=("all", "2015-10-21", "2020-10-21"))
    df_360 = pd.read_sql(queryCatPerRange, db.connection, params=("360", "2019-10-21", "2020-10-21"))
    df_30 = pd.read_sql(queryCatPerRange, db.connection, params=("30", "2020-09-21", "2020-10-21"))

    # print(df_Total)
    # print(df_360)
    # print(df_30)

    df_days = pd.concat([df_Total, df_360, df_30])
    # print(df_days)
    df_days_mod = df_days.pivot(index="Zeitraum", columns="Kategorie", values="Total").fillna(0)

    # axpie
    # exit(0)
    # ------------------------------------------------------------------------------------------
    # SALDO
    queryDaysum = ("SELECT datum as Datum, SUM(betrag) as Saldo FROM buchung GROUP BY datum ORDER BY datum ASC")

    query = db.cursor.execute(queryDaysum)
    headers = [i[0] for i in db.cursor.description]
    data = {}
    first = True
    for result in query:
        for idx, name in enumerate(headers):
            if first:
                if name == "Saldo":
                    # diff = (data["Saldo"][-1] - float(session.balance))
                    data[name] = [result[idx]-952]
                else:
                    data[name] = [result[idx]]
            else:
                if name == "Saldo":
                    previous_val = data[name][-1]
                    data[name].append(result[idx]+previous_val)
                else:
                    data[name].append(result[idx])
        first = False

    df_saldo = pd.DataFrame(data)
    # ------------------------------------------------------------------------------------------

    fig, axes = plt.subplots(nrows=2, ncols=2)

    df_y_mod.plot(kind="bar", ax=axes[0, 0])
    df_m_mod.plot(kind="bar", ax=axes[0, 1], stacked="True")
    df_saldo.plot(ax=axes[1, 0])

    # df_days_mod.info()
    # df_days_mod.apply(lambda x: x*100/sum(x), axis="Total")
    #df_days_mod.plot(kind="bar", ax=axes[1,0], stacked="True")
    # print(df_days.Total)
    plt.pie(df_days.Total)

    size = 0.3
    # vals = np.array([[60., 32.], [37., 40.], [29., 10.]])
    # vals = df_days_mod

    # cmap = plt.get_cmap("tab20c")
    # outer_colors = cmap(np.arange(3)*4)
    # inner_colors = cmap(np.array([1, 2, 5, 6, 9, 10]))

    # axes.pie(vals.sum(axis=1), radius=1, colors=outer_colors,
    #     wedgeprops=dict(width=size, edgecolor='w'))

    # axes.pie(vals.flatten(), radius=1-size, colors=inner_colors,
    #     wedgeprops=dict(width=size, edgecolor='w'))

    # axes.set(aspect="equal", title='Pie plot with `ax.pie`')

    plt.show()

    return 0
