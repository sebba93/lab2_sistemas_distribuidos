from time import sleep
from json import dumps
from kafka import KafkaProducer
#Abrir archivo csv
import csv
#api
from zeep import Client, Settings, xsd
from zeep.plugins import HistoryPlugin

STATION_CODES_FILENAME = "data/station_codes.csv"
LDB_TOKEN = '51f9165f-6819-4e8a-a9b3-194fb0f4d91a'
WSDL = 'http://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2021-11-01'

#----------------------- Definiciones -----------------------#
def get_stations(archivo):
    #Leer archivo de código de estaciones
    with open(archivo) as stations:
        reader = csv.reader(stations)
        next(reader, None)  #Salto del nombre
        codigos = {}
        for row in reader:
            codigos[row[1]] = row[0]

    return codigos


def get_services_from_dep_board(codigo, cantServicio):
    #numrows = cantidad de datos (0 a 150)
    #crs = codigo de la estacion http://www.nationalrail.co.uk/stations_destinations/48541.aspx
    res = client.service.GetDepBoardWithDetails(numRows=cantServicio,
                                       crs=codigo,
                                       _soapheaders=[header_value])
    print("Trains at " + res.locationName)
    print("===============================================================================")

    if res.trainServices is None:
        return "No hay servicio"

    trainServices = res.trainServices.service

    for t in trainServices:
        data = {'locationName': res.locationName,
                'tiempoProgramadoSalida': t.std,
                'destinationName': t.destination.location[0].locationName,
                'tiempoEstimadoSalida': t.etd}
        print(t.std + " to " + t.destination.location[0].locationName + " - " + t.etd)
        producer.send('topic_test', value=data)
    return "\nServicio conseguido"

#----------------------- Bloque principal -----------------------#
#iniciar api
if LDB_TOKEN == '':
    raise Exception("Please configure your OpenLDBWS token in getDepartureBoardExample!")

settings = Settings(strict=False)

history = HistoryPlugin()

client = Client(wsdl=WSDL, settings=settings, plugins=[history])

header = xsd.Element(
    '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken',
    xsd.ComplexType([
        xsd.Element(
            '{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue',
            xsd.String()),
    ])
)
header_value = header(TokenValue=LDB_TOKEN)

#Conseguir codigos para la api
estaciones = get_stations(STATION_CODES_FILENAME)

#productor
producer = KafkaProducer(
    bootstrap_servers=['kafka:9093'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

for estacion in estaciones:
    try:
        print(get_services_from_dep_board(estacion,40))
    except:
        print("No existe "+estacion)

