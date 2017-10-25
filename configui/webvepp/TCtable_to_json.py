__author__ = 'oidin'
import json
import inspect, os
from collections import OrderedDict

def getTextFile(name):
    data = open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name)
    return data

def make_custom_sort(orders):
    orders = [{k: -i for (i, k) in enumerate(reversed(order), 1)} for order in orders]
    def process(stuff):
        if isinstance(stuff, dict):
            l = [(k, process(v)) for (k, v) in stuff.items()]
            keys = set(stuff)
            for order in orders:
                return OrderedDict(sorted(l, key=lambda x: order.get(x[0], 0)))
            return OrderedDict(sorted(l))
        if isinstance(stuff, list):
            return [process(x) for x in stuff]
        return stuff
    return process


def identifySensorType(sensorname):
    if "SW" in sensorname:
        return "Blocking sensor"
    else:
        return "Measuring sensor"


def saveJson(objects,name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name, 'w') as outfile:
        json.dump(objects,outfile,indent=4, separators=(',', ': '))

def getDataFile(name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name) as data_file:
        data = json.load(data_file)
    return data


def findElement(elements,name):
    result = next((x for x in elements if x["Name"] == name), None)
    return result


def to_int(string):
    if string=="NUL":
        return None
    else:
        return int(string)

def to_float(string):
    if string=="NUL":
        return None
    else:
        return float(string)


def makeControllerObject(line,systemname):
    element = {}
    element["Class"] = "Controller"
    element["Name"] = line[3].strip()
    element["System"] = systemname
    element["Address"] = to_int(line[2].strip())
    element["Position"] = ""
    element["Comment"] = ""
    return element


def makeLoopObject(line,controller,systemname):
    element = {}
    element["Class"] = "Line"
    element["Name"] = line[4].strip()
    element["Controller"] = controller.strip()
    element["System"] = systemname
    element["Comment"] = ""
    element["Sensors"] = [{
        identifySensorType(line[1].strip()): line[1].strip(),
        "Position": to_int(line[5].strip())
    }]
    return element

def addSensorToLoop(line,loop):
    loop["Sensors"].append({
        identifySensorType(line[1].strip()): line[1].strip(),
        "Position": to_int(line[5].strip())
    })


def makeSensorObject(line,systemname):
    element = {}
    element["Class"] = identifySensorType(line[1].strip())
    element["Name"] = line[1].strip()
    element["Comment"] = ""
    element["System"] = systemname
    element["Bank number"] = to_int(line[6].strip())
    element["Full name"] = line[7].strip()
    element["Position"] = ""
    if element["Class"] == "Blocking sensor":
        element["Alarm"] = to_int(line[8].strip())
        element["RelayAlarm"] = to_int(line[9].strip())
        element["PowerOff"] = to_int(line[10].strip())
        element["RelayOff"] = to_int(line[11].strip())
    return element


def parseFile(systemname):
    file_txt = getTextFile(systemname+"Tsensor.txt")
    controllers = []
    loops = []
    sensors = []
    controller_names = []
    loop_ids = []
    controller_sort = make_custom_sort([["Class", "Name", "System", "Comment", "Address", "Position"]])
    loop_sort = make_custom_sort([["Class", "Name", "Controller", "System", "Comment","Sensors"]])
    sensor_sort = make_custom_sort([["Class", "Name", "System", "Comment", "Bank number", "Full name", "Position", "Alarm", "RelayAlarm", "PowerOff", "RelayOff"]])
    for line_txt in file_txt:
        line_splitted = line_txt.split("|")
        if line_splitted[3] not in controller_names:
            controller = makeControllerObject(line_splitted,systemname)
            loop = makeLoopObject(line_splitted,line_splitted[3],systemname)
            controllers.append(controller)
            loops.append(loop)
            loop_ids.append(line_splitted[3]+line_splitted[4])
            controller_names.append(line_splitted[3])
        elif line_splitted[3]+line_splitted[4] not in loop_ids:
            loop = makeLoopObject(line_splitted,line_splitted[3],systemname)
            loops.append(loop)
            loop_ids.append(line_splitted[3]+line_splitted[4])
        else:
            addSensorToLoop(line_splitted,loops[-1])
        sensor = makeSensorObject(line_splitted,systemname)
        sensors.append(sensor)
    sorted_elements = controller_sort(controllers)
    sorted_elements += loop_sort(loops)
    sorted_elements += sensor_sort(sensors)
    return sorted_elements


elements = parseFile("V4")
elements += parseFile("V3")
saveJson(elements,"TC.json")