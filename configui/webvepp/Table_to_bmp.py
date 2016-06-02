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
                #if keys.issuperset(order):
                    return OrderedDict(sorted(l, key=lambda x: order.get(x[0], 0)))
            return OrderedDict(sorted(l))
        if isinstance(stuff, list):
            return [process(x) for x in stuff]
        return stuff
    return process

def abbr_to_group(argument):
    switcher = {
        "MAGS": "Magnetic System",
        "ELST": "Electrostatics",
        "RFRF": "RF System",
        "DOPM": "Measurements",
        "URUR": "Relays"
    }
    return switcher.get(argument, "")

def abbr_to_type(argument):
    switcher = {
        "OSST": "Main Structure",
        "NELN": "Non-linearity Correction",
        "COOR": "Orbit Correction",
        "COGR": "Gradient Correction",
        "ELST": "Electrostatics",
        "RFRF": "RF System",
        "DOPM": "Measurements"
    }
    return switcher.get(argument, "")

def abbr_to_boolean(argument):
    switcher = {
        "T": True,
        "F": False
    }
    return switcher.get(argument, True)

def abbr_to_channel(argument):
    switcher = {
        "C": "Control channel",
        "A": "ADC channel",
        "U": "UR channel"
    }
    return switcher.get(argument, "")

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

def makeBPMObject(line):
    bmp = {}
    bmp["Class"] = "BMP"
    bmp["Name"] = line[0]
    bmp["System"] = "V4"
    bmp["Comment"] = ""
    bmp["BMP Type"] = to_int(line[1])
    bmp["Azimuth"] = to_float(line[2])
    bmp["GX"] = to_float(line[3])
    bmp["GZ"] = to_float(line[4])
    bmp["GeodX"] = to_float(line[5])
    bmp["GeodZ"] = to_float(line[6])
    bmp["X0"] = to_float(line[7])
    bmp["Z0"] = to_float(line[8])
    return bmp

def findElement(elements,name):
    result = next((x for x in elements if x["Name"] == name), None)
    return result

def saveJson(objects,name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name, 'w') as outfile:
        json.dump(objects,outfile,indent=4, separators=(',', ': '))

def getDataFile(name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name) as data_file:
        data = json.load(data_file)
    return data


file_txt = getTextFile("bpm.data")
py_bpms = []
custom_sort = make_custom_sort([["Class", "Name", "System", "Comment", "BMP Type", "Azimuth", "GX", "GZ", "GeodX", "GeodZ", "X0", "Z0"]])
for line_txt in file_txt:
    line_splitted = line_txt.split()
    py_object = makeBPMObject(line_splitted)
    py_bpms.append(py_object)
bpms = custom_sort(py_bpms)
saveJson(bpms,"bpm.json")