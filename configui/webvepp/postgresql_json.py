__author__ = 'oidin'
import psycopg2
import json
import os
from collections import OrderedDict


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

def saveJson(objects,name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name, 'w') as outfile:
        json.dump(objects,outfile,indent=4, separators=(',', ': '))


conn = psycopg2.connect("dbname=v4parameters user=vepp4 host=vepp4-pg port=5432")
cur = conn.cursor()
#cur.execute('SELECT * FROM ...')
#circ = cur.fetchall()
cur.execute('SELECT contr_name, contr_addr, contr_place, status FROM "T_controller"')
contr = cur.fetchall()
cur.execute('SELECT full_name, unit, relay_warning, "Twarning", relay_poweroff, "Tpoweroff", contr_addr, param_addr, status FROM "T_sensor"')
sens = cur.fetchall()
cur.close()

conn.close()


"""circuit_sort = make_custom_sort([["Class", "Name", "Type", "Comment", "Controllers"]])
controller_sort = make_custom_sort([["Class", "Name", "Place","Address", "Status", "Comment", "Block_sensors", "Meas_sensors", "Sensors"]])
sensor_sort = make_custom_sort([["Class", "Name", "Type","Address", "Status", "Comment", "Rwarning", "Twarning", "Rpoweroff", "Tpoweroff"]])
circuits_sorted = circuit_sort(circuits)
controllers_sorted = controller_sort(controllers)
sensors_sorted = sensor_sort(sensors)
elements = circuits_sorted + controllers_sorted + sensors_sorted
saveJson(elements,"Termocontroll.json")"""

