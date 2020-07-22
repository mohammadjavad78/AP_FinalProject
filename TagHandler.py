import csv
import time

# Just reading tags
with open('TagSample1.csv', mode = 'r+') as f:
    data = csv.reader(f)
    dataL = list(data)
    
# Inserting new tags or updating same tags
tag = input("TAG?\n")
times = input("TIME? IN H:M:S Format\n")
x = time.strptime(times, "%H:%M:%S")
tagTime = time.strftime("%H:%M:%S", x)


with open('TagSample1.csv', mode = 'r+') as f:
    data = csv.reader(f)
    dataL = list(data)
    i = 0
    flag = False

    while tagTime > dataL[i][1]:
        i += 1
        if i >= len(dataL):
            break

    if i < len(dataL):
        if tagTime == dataL[i][1]:
            dataL[i] = [tag, tagTime]
            flag = True

    if not flag:
        dataL.insert(i, [tag, tagTime])

    f.seek(0)
    writer = csv.writer(f, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL, lineterminator='\n')
    for line in dataL:
        writer.writerow(line)