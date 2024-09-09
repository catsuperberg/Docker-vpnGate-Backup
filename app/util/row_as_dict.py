def row_as_dict(row, header):
    return dict(zip(header, row.split(",")))
