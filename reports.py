import sqlite3
import pandas as pd



def final_report(**kwargs):
    # connect to the SQLite database
    conn = sqlite3.connect("statement.sqlite")

    # get a list of table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    today_sql = kwargs.get("time")
    # create a pandas Excel writer object
    writer = pd.ExcelWriter(
        f"reports/withdrawal_report_{today_sql}.xlsx", engine="xlsxwriter"
    )

    # loop through each table and write it to a separate sheet in the Excel file
    for table_name in tables:
        table_name = table_name[0]
        if today_sql in table_name:
            df = pd.read_sql(f"SELECT * from {table_name}", conn)
            max_len = [max([len(str(x)) for x in df[col]]) for col in df.columns]
            df.to_excel(writer, sheet_name=table_name[:-11], index=False)
            worksheet = writer.sheets[table_name[:-11]]
            for i, width in enumerate(max_len):
                worksheet.set_column(i, i, width + 2)
    # save the Excel file
    writer._save()

    # close the SQLite connection
    conn.close()
    print("Withdrawal report is ready to use.")
