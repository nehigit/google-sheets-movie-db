from MovieSheet import MovieSheet


ms = MovieSheet()

for row_id in range(2, ms.used_rows + 1):
    ms.update_row(row_id)