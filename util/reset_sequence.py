from django.db import connection

def reset_sequence(model):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT setval(pg_get_serial_sequence('{model._meta.db_table}', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM {model._meta.db_table};")
