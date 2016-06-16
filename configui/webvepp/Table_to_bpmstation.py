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

def makeRecieverObject(line):
    obj = {}
    obj["Class"] = "Module"
    obj["Name"] = line[0]+"BPMC"
    obj["Module Type"] = "BPMcontroller"+line[5]
    obj["System"] = "V4"
    obj["Comment"] = ""
    obj["BMP"] = line[1]
    obj["IP"] = line[2]
    obj["Port"] = to_int(line[3])
    obj["MAC"] = line[4]
    obj["GI"] = to_float(line[6])
    obj["g0_button0"] = to_float(line[7])
    obj["g0_button1"] = to_float(line[8])
    obj["g0_button2"] = to_float(line[9])
    obj["g0_button3"] = to_float(line[10])
    obj["g1_button0"] = to_float(line[11])
    obj["g1_button1"] = to_float(line[12])
    obj["g1_button2"] = to_float(line[13])
    obj["g1_button3"] = to_float(line[14])
    obj["g0_gI"] = to_float(line[15])
    obj["g1_gI"] = to_float(line[16])
    obj["Date"] = line[17]
    return obj

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


file_txt = getTextFile("station.data")
py_recievers = []
custom_sort = make_custom_sort([["Class", "Name", "Module Type", "System", "Comment", "BMP", "IP", "Port", "MAC", "GI", "g0_button0", "g0_button1", "g0_button2", "g0_button3", "g1_button0", "g1_button1", "g1_button2","g1_button3", "g0_gI", "g1_gI", "Date"]])
for line_txt in file_txt:
    line_splitted = line_txt.split()
    py_object = makeRecieverObject(line_splitted)
    py_recievers.append(py_object)
bpms = custom_sort(py_recievers)
saveJson(bpms,"station.json")