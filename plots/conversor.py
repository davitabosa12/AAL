import csv
import numpy as np
import pandas
with open("heatmapPaulo.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    data = np.array()
    print("Reading...")
    row_count = 0
    for row in csv_reader:
        col_count = 0
        arr = np.array()
        pandas.DataFrame()
        for num in row:
            arr.to
            arr.append(int(num))
            col_count += 1
            
    data.append()