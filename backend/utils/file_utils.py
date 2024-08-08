import csv
import zipfile
from io import StringIO, BytesIO


# def query_to_dict_list(query_result):
#     result_list = []
#     for row in query_result:
#         row_dict = row.__dict__
#         row_dict.pop('_sa_instance_state', None)  # Remove SQLAlchemy state key
#         result_list.append(row_dict)
#     return result_list
#
#
# def generate_csv(data):
#     if not data:
#         yield ''
#         return
#
#     output = StringIO()
#     keys = data[0].keys()
#     dict_writer = csv.DictWriter(output, fieldnames=keys)
#     dict_writer.writeheader()
#     for row in data:
#         dict_writer.writerow(row)
#     return output


def query_to_csv(query_result):
    """
    Convert SQLAlchemy query result to a CSV string.

    :param query_result: SQLAlchemy query result (list of ORM instances)
    :return: CSV string in a StringIO object
    """
    if not query_result:
        return StringIO()  # Return empty CSV if no results

    # Dynamically get headers from the first result's attributes
    headers = query_result[0].__table__.columns.keys()

    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Write headers
    csv_writer.writerow(headers)

    # Write rows
    for row in query_result:
        csv_writer.writerow([getattr(row, header) for header in headers])

    csv_buffer.seek(0)
    return csv_buffer


def create_zip_from_csvs(csv_files):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in csv_files:
            zip_file.writestr(filename, csv_files[filename].getvalue())

    zip_buffer.seek(0)
    return zip_buffer
