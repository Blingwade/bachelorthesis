import numpy

numpy.random.seed(1)
datapoints = 1000
influxdata = [list(),list(),list()]
postgresqldata = [list(),list(),list()]
pure = numpy.linspace(0, 100, datapoints)
# pure2 =[]
print(numpy.random.choice([True,False]))
saturation = 0.5
for j in range(3):
    saturationarray = []
    for i in range(datapoints):
        saturationarray.append([[numpy.random.choice([True,False], p = [saturation,1-saturation])],[[numpy.random.choice([True,False],p = [saturation,1-saturation])]],[[numpy.random.choice([True,False],p = [saturation,1-saturation])]]])

    # [[True][False][False]]
    for n in range(datapoints):
        table = numpy.random.choice([0,1,2])
        noise1 = numpy.random.normal(0, 1)
        # pure2.append(pure[n]+noise1)
        noise2 = numpy.random.normal(0, 1)
        noise3 = numpy.random.normal(0, 1)
        signal1 = str(pure[n] + noise1) if saturationarray[n][0]==numpy.True_ else ""
        signal2 = str(pure[n] + noise2) if saturationarray[n][1]==numpy.True_ else ""
        signal1comma = ""
        signal2comma = ""
        signal3comma = ""
        if(signal1!="" and signal2!=""):
            signal1comma += ","
        signal3 = str(pure[n] + noise3) if saturationarray[n][2]==numpy.True_ else ""
        if(signal2!="" and signal3!=""):
            signal2comma += ","
        if(signal1!="" and signal3!="" and signal2==""):
            signal1comma += ","
        
        influxsignal1 = "field1=" + signal1 if signal1 != "" else ""
        influxsignal2 = "field2=" + signal2 if signal2 != "" else ""
        influxsignal3 = "field3=" + signal3 if signal3 != "" else ""

        if not (signal1=="" and signal2 =="" and signal3== ""):
            influxdata[j].append( "example_measurement"+ str(table) + ",tag1=example_tag "+ influxsignal1 + signal1comma + influxsignal2  + signal2comma + influxsignal3 + " " + str(1641024000 + 10*n) + "\n")
            postgresqldata[j].append("example_measurement"+ str(table) +  ",example_tag," + (signal1 + "," if signal1!="" else "NULL,") + (signal2 + "," if signal2!="" else "NULL,") + (signal3 + "," if signal3!="" else "NULL,") + str(1641024000 + 10*n) + "\n")
        if n % 100 == 0:
            print(str(n) + "/" + str(datapoints))
print("writitng")

def write_to_file(path, data_list):
    f = open(path, "w")
    for data in data_list:
        f.write(data)
    f.close()

write_to_file("influxdata0.txt", influxdata[0])
write_to_file("influxdata1.txt", influxdata[1])
write_to_file("influxdata2.txt", influxdata[2])
write_to_file("postgresqldata0.txt", postgresqldata[0])
write_to_file("postgresqldata1.txt", postgresqldata[1])
write_to_file("postgresqldata2.txt", postgresqldata[2])

#f = open("influxdata0.txt", "w")
#f.write(influxdata[0])
#f.close()
#f = open("influxdata1.txt", "w")
#f.write(influxdata[1])
#f.close()
#f = open("influxdata2.txt", "w")
#f.write(influxdata[2])
#f.close()
#
#f = open("postgresqldata0.txt", "w")
#f.write(postgresqldata[0])
#f.close()
#
#f = open("postgresqldata1.txt", "w")
#f.write(postgresqldata[1])
#f.close()
#
#f = open("postgresqldata2.txt", "w")
#f.write(postgresqldata[2])
#f.close()

#import matplotlib.pyplot as plt

#plt.plot(pure2)
#plt.ylabel('some numbers')
#plt.savefig("example.png")

#INSERT INTO example_table1 (tag1, field1, field2, field3, timestamp)
        #VALUES (%s, %s, %s, %s, %s);