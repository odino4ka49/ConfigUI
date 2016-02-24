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
    channel["System"] = "V4"
    channel["BANK"] = to_int(line[3])
    channel["Module"] = line[4]
    channel["Channel"] = to_int(line[5])
    channel["Cod/Value"] = to_float(line[6])
    channel["Units"] = line[7]
    channel["Max"] = to_float(line[8])
    channel["Monit"] = abbr_to_boolean(line[9])
    channel["MonitType"] = line[10]
    channel["Deviation"] = to_float(line[11])
    """for index in range(4,4+int(line[3]),2):
        element["Channels"].append({
            "OK": True,
            abbr_to_channel(line[index+1]): line[index]
        })"""
    return channel

def addAttributesToElement(element,line):
    element["Efficiency"] = to_float(line[12])
    element["Location"] = to_int(line[13])
    element["Resistance"] = to_float(line[14])

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


file_txt = getTextFile("V4CH.koi")
py_channels = []
elements = getDataFile("V4el.json")
custom_sort = make_custom_sort([["Class", "Name", "Element", "System", "Comment", "BANK", "Module", "Channel", "Cod/Value", "Units", "Max", "Monit", "MonitType", "Deviation"]])
el_sort = make_custom_sort([["Class","Name","System","Group","Type","Comment","Polarity","Resistance", "Efficiency", "Location","Channels"]])
for line_txt in file_txt:
    line_splitted = line_txt.split()
    py_object = makeChannelObject(line_splitted)
    if line_splitted[2]=="C":
        addAttributesToElement(findElement(elements,line_splitted[0]),line_splitted)
    py_channels.append(py_object)
channels = custom_sort(py_channels)
#saveJson(channels,"V4ch.json")
elements_sorted = el_sort(elements)
saveJson(elements_sorted,"V4eladd.json")