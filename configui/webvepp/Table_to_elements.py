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
    element["Channels"] = []
    for index in range(4,3+int(line[3])*2,2):
        element["Channels"].append({
            "OK": True,
            abbr_to_channel(line[index+1]): line[index]
        })
    return element

def saveJson(objects,name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name, 'w') as outfile:
        json.dump(objects,outfile,indent=4, separators=(',', ': '))


file_txt = getTextFile("v4el.txt")
py_elements = []
custom_sort = make_custom_sort([["Class","Name","System","Group","Type","Comment","Channels"]])
for line_txt in file_txt:
    line_splitted = line_txt.split()
    py_object = makeElementObject(line_splitted)
    py_elements.append(py_object)
py_elements = custom_sort(py_elements)
saveJson(py_elements,"V4el.json")
