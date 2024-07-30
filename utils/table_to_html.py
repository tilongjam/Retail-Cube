def table_to_html(data, columns):
    heading = "<thead><tr>"
    for i in range(len(columns)):
        col = columns[i]
        if i == len(columns) - 1:
            heading += f"<th>{col}</th></tr></thead>"
        else:
            heading += f"<th>{col}</th>"
    body = "<tbody>"

    for i in range(len(data)):
        body += "<tr>"
        for j in range(len(columns)):
            val = data.loc[i, columns[j]]
            if j == 0:
                cell = f"<td class='clickable-td' style='text-align: center;'><a href='#' style='color: white; text-decoration: none;'>{val}</a></td>"
            else:
                try:
                    val = f"{round(float(val), 2):,}"
                except Exception as e:
                    print(e)
                cell = f"<td style='text-align: center;'>{val}</td>"

            body += cell
        body += "</tr>"
    body += "</tbody>"

    final_table = f"<table class='table table-striped sortable'>{heading}{body}</table>"
    return final_table



def table_to_html_select(data, columns, select_cols=[]):
    heading = "<thead><tr>"
    for i in range(len(columns)):
        col = columns[i]
        if i == len(columns) - 1:
            heading += f"<th>{col}</th></thead></tr>"
        else:
            heading += f"<th>{col}</th>"
    body = "<tbody>"

    for c in select_cols:
        select_str = f"<td><select>"
        options = data[c].unique()
        for option in options:
            select_str += f"<option val='{option}'>{option}</option>"
        select_str += "</select></td>"
    for i in range(len(data)):
        body += "<tr>"
        for j in range(len(columns)):
            val = data.loc[i, columns[j]]
            if columns[j] in select_cols:
                select_str = "<select class='select2-single table_select'>"
                options = data[c].unique()
                for option in options:
                    if option == val:
                        select_str += (
                            f"<option val='{option}' selected>{option}</option>"
                        )
                    else:
                        select_str += f"<option val='{option}'>{option}</option>"
                select_str += "</select>"
                cell = f"<td>{select_str}</td>"
            else:
                if j == 0:
                    cell = f"<td><a href='#' style='color: white; text-decoration: none;'>{val}</a></td>"
                else:
                    try:
                        val = f"{round(float(val), 2):,}"
                    except Exception as e:
                        print(e)
                    cell = f"<td>{val}</td>"
            body += cell
        body += "</tr>"
    body += "</tbody>"

    final_table = (
        f"""<table class='table table-striped sortable'>{heading}{body}</table>"""
    )
    return final_table
