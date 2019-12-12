import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import pandas
import math


def isDark(color):
    r = color[0]
    g= color[1]
    b = color[2]
    hsp = math.sqrt(
        0.299 * (r * r) +
        0.587 * (g * g) +
        0.114 * (b * b)
    )
    return hsp < 0.5

    

# with open("log.csv") as csv_file:
#    csv_reader = csv.reader(csv_file, delimiter=';')
#    line_count = 0
#    data_bytes = []
#    print("Reading...")
#    for row in csv_reader:
#
#        data_to_send = data_pb2.Data()
#
#        data_to_send.Entity_Id = 101
#        data_to_send.Location = row[2]
#        data_to_send.Timestamp = row[0]
#
#        data_bytes.append(data_to_send.SerializeToString())
#    print('Data read.')
data = []
linhas = ["Framework", "Middleware", "Platform", "Architecture",
          "System", "Approach", "Engine", "Robot Services"]
cols = ["Older adults needs", "Heterogeneity", "Interoperability", "Context Awareness","Security",
        "Scalability", "Usability", "Reliability", "Power Management", "Privacy", "Effectiveness", "Extensibility", "foo", "foo2", "foodeo"]
with open("heatmapPaulo.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')

    for row in csv_reader:
        arr = []
        for num in row:
            arr.insert(len(arr), int(num))
        data.insert(len(data), arr)
#print(data)
df = pandas.DataFrame(data, columns=cols, index=linhas)
print(df)
#df.pivot(index= linhas, columns= cols, values=data)
#ax = sns.heatmap(df, annot=True, fmt='d', cmap="YlOrRd")
plain_list = []
for lista in data:
    for num in lista:
        plain_list.append(num)
x = np.array(list(np.arange(len(cols))) * len(linhas))
y = np.array(list(np.arange(len(linhas))) * len(cols))
#organizar o eixo y para agrupar os digitos.
y.sort()
#transformar a list em np.array
plain_list = np.array(plain_list)
#grafico de scatter (bubble heat map)
plt.tick_params(axis='both', length=0.1, width=0.1)

#COLOR MAP
color_map = 'Blues'


plt.scatter(x, y, s= plain_list * 200, c=plain_list, cmap=color_map)
#inverter o eixo Y
plt.gca().invert_yaxis()

#renomear os ticks
plt.xticks(np.arange(len(cols)), cols, rotation=40)
plt.yticks(np.arange(-1, len(linhas) + 1), ["",*linhas])
ax = plt.gca()
#annotations
x_pos =0
y_pos = 0
gnuplot = cm.get_cmap(color_map, 6)

for lista in data:
    x_pos = 0
    for num in lista:
        if(isDark(gnuplot(num))):
            ax.annotate(xy=[x_pos, y_pos], s=num, ha='center', va='center', c='white')
        else:
            ax.annotate(xy=[x_pos, y_pos], s=num, ha='center', va='center', c='black')
        x_pos += 1
    y_pos += 1
    
print(f"x:{x_pos}, y:{y_pos}")
figs = plt.gcf()

figs.set_size_inches(10.24, 7.68)
plt.colorbar()
plt.savefig("graf.png")

plt.show()
