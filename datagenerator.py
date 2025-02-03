import numpy

numpy.random.seed(1)

influxdata = ""
postgresqldata = ""
pure = numpy.linspace(0, 100, 100)

for n in range(100):

    noise1 = numpy.random.normal(0, 1)
    noise2 = numpy.random.normal(0, 1)
    noise3 = numpy.random.normal(0, 1)
    signal1 = pure[n] + noise1
    signal2 = pure[n] + noise2
    signal3 = pure[n] + noise3

    influxdata = influxdata + "example_measurement,tag1=example_tag field1="+str(signal1) +",field2=" + str(signal2) + ",field3=" + str(signal3) + " " + str(1641024000 + n) + "\n"
    postgresqldata = postgresqldata + "\'example_tag\'," + str(signal1) + "," + str(signal2) + "," + str(signal3) + "," + str(1641024000+n) + "\n"
print(influxdata)

f = open("data.txt", "w")
f.write(influxdata)
f.close()

f = open("postgresqldata.txt", "w")
f.write(postgresqldata)
f.close()
