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
                if keys.issuperset(order):
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

def makeElementObject(line):
    element = {}
    element["Class"] = "Element"
    element["Name"] = line[0]
    element["System"] = "V4"
    element["Group"] = abbr_to_group(line[1])
    element["Type"] = abbr_to_type(line[2])
    element["Comment"] = None
    element["Polarity"] = None
    element["Channels"] = []
    for index in range(4,4+int(line[3]),2):
        element["Channels"].append({
            "OK": True,
            abbr_to_channel(line[index+1]): line[index]
        })
    return element

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

def makeChannelObject(line):
    channel = {}
    channel["Class"] = abbr_to_channel(line[2])
    channel["Name"] = line[1]
    channel["Element"] = line[0]
    channel["Comment"] = ""
    channel["System"] = abbr_to_group(line[1])
    channel["BANK"] = to_int(line[3])
    channel["Module"] = line[4]
    channel["Channel"] = []
    channel["Channel ON"] = []
    index = 6
    while line[index]!="ON":
        channel["Channel"].append(to_int(line[index]))
        index+=1
    index+=1
    while index<len(line):
        channel["Channel ON"].append(to_int(line[index]))
        index+=1
    return channel

def saveJson(objects,name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name, 'w') as outfile:
        json.dump(objects,outfile,indent=4, separators=(',', ': '))


file_txt = getTextFile("V4chUR.koi")
py_channels = []
custom_sort = make_custom_sort([["Class", "Name", "Element", "System", "Comment", "BANK", "Module", "Channel", "Channel ON"]])
for line_txt in file_txt:
    line_splitted = line_txt.split()
    py_object = makeChannelObject(line_splitted)
    py_channels.append(py_object)
channels = custom_sort(py_channels)
saveJson(channels,"V4ur.json")