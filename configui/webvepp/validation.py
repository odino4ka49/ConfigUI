__author__ = 'oidin'
import json
import inspect, os


def getDataFile(name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name) as data_file:
        data = json.load(data_file)
    return data

file_name = "CHAN.json"
file_output_name = file_name.replace('json','txt')
objects = getDataFile(file_name)
py_channels = []

saveJson(elements_sorted,"V4eladd.json")