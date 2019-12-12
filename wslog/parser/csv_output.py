import csv
import os
def txt_to_csv(file):
    to_save = {
        "time_send": 0,
        "time_recv" : 0,
        "time_delta" : 0
    }
    with open(str(file) + ".csv", 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        with open(file) as txt_file:
            lines = txt_file.readlines()
            for line in lines:
                exploded = line.split(' ')
                decimals = []
                
                for splitted in exploded:
                    print(splitted)
                    try:
                        num = float(splitted)
                        if(num % 1 != 0):
                            decimals.append(num)
                    except:
                        pass
                continue
                to_save["time_send"] = decimals[1]
                to_save["time_recv"] = decimals[0]
                to_save["time_delta"] = to_save["time_send"] - to_save["time_recv"]
                csv_writer.writerow(to_save)
            
            


if __name__ == "__main__":
    for file in os.listdir():
        if('.txt' in file):
            txt_to_csv(file)
            

