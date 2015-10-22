from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import json
import inspect, os


def index(request):
    template = loader.get_template('webvepp/index.html')
    return HttpResponse(template.render())

def getTreeData(request):
    try:
        tree = {"name":"CHAN","id":"8","_parents":[],"attributes":{"min":[{"key":"System","value":"CHAN"}],"extra":[]}}
        file_data = getAllObjects()
        camac_list = getOneClass("CAMAC")
        for camac in camac_list:
            tree["_parents"].append(parseObject(camac))
    except Exception as e:
        print e
    return HttpResponse(json.dumps(tree, ensure_ascii=False), content_type="application/json")

#returns packed object
def parseObject(object):
    #if "link_id" in object:
        #result = {"name":object["Name"],"id":object["Name"],"link_id":object["link_id"],"_parents":[]}
    result = {"name":object["Name"],"id":object["Name"],"_parents":[]}
    template = getTemplate(object)
    obj_attributes = parseAttributes(template,object)
    result["attributes"]=obj_attributes
    if template["components"]:
        for comp in object[template["components"]]:
            comp_class = ""
            for key in comp:
                if key in template["component_types"]:
                    comp_class = key
            comp_temp = getTemplate({"Class":comp_class})
            rules = {}
            rules["Class"] = comp_class
            for i in range(0,len(comp_temp["primary_keys"])-1):
                field1 = template["component_check_values"][i]
                field2 = comp_temp["primary_keys"][i]
                rule_val = None
                if field1=="Component_name":
                    rule_val = comp[comp_class]
                elif comp[field1]:
                    rule_val = comp[field1]
                else:
                    rule_val=object[field1]
                rules[field2] = rule_val
            comp_obj = getObject(rules)
            #if we do number of position on link:
            comp_obj["link_id"] = comp[template["component_ID"]]
            result["_parents"].append(parseObject(comp_obj))
    return result

#returns list of attributes of the object according to its template
def parseAttributes(template,object):
    attributes = {"min":[],"extra":[]}
    def parsing(field_list):
        attrs = []
        for field in field_list:
            if (type(field) is dict) and ('link_to' in field) and ('link_from' in field):
                print field
                #rules = parseRulesToString(object,field['link_from'])
                obj1 = getObject(parseRulesToString(object,field['link_from']))
                obj2 = getObject(parseRulesToString(object,field['link_to']))
                if obj2 and obj1:
                    link = getLink(obj1,obj2)
                    attrs += [{
                        "key": field["key"],
                        "value": link[field["value"]]
                    }]
            elif (type(field) is dict) and ('link_to' in field):
                #if we do this channels->id thing
                rules = parseRulesToString(object,field['link_to'])
                obj2 = getObject(rules)
                if obj2:
                    link = getLink(object,obj2)
                    attrs += [{
                        "key": field["key"],
                        "value": link[field["value"]]
                    }]
            elif (type(field) is dict) and ("value" in field) and (field["value"]=="link_id") and ("link_id" in object):
                attrs += [{
                        "key": field["key"],
                        "value": object["link_id"]
                    }]
            else:
                attrs += [{
                    "key": field,
                    "value": object[field]
                }]
        return attrs

    if("display_fields" in template):
        attributes["min"] = parsing(template["display_min"])
        attributes["extra"] = parsing(template["display_fields"])
    else:
        for field in template["fields"]:
            field_name = field["key"]
            attributes["min"] += [{
                "key": field_name,
                "value": object[field_name]
            }]
    return attributes

def getCamac(request):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/CHAN.json') as data_file:
        data = json.load(data_file)
    camac_list = getOneClass(data,"CAMAC")
    return HttpResponse(json.dumps(camac_list, ensure_ascii=False), content_type="application/json")

def getClassTemplate(classname):
    file_data = getAllTemplates()
    for temp in file_data:
        if(temp["class"]==classname):
            return temp

def findObject(array,check_object,check_rules):
    result_object = {"Channels":[{"ID":8}]}
    for object in array:
        for check_field in check_rules:
            #if(object[check_field]==check_object[check_rules[check_field].replace("&", "")]):
                print "hohoh"
    return result_object

def getAllTemplates():
    return getDataFile("Chan_template.json")

def getAllObjects():
    return getDataFile("CHAN.json")

def getObject(rules):
    object = {}
    data = getAllObjects()
    def filter(o):
        result = True
        for r in rules:
            """ if we use '->':
            deep_r = r.split("->")
            o_value = o
            for i in range(0,len(deep_r)-1):
                if deep_r[i] in o_value:
                    o_value = o_value[deep_r[i]]
                else:
                    result = False
            if (o_value!=rules[r]):
                result = False"""
            if r in o and o[r]!=rules[r]:
                result = False
        return result
    for obj in data:
        if(filter(obj)):
            object = obj
    return object

def getTemplate(object):
    templates = getAllTemplates()
    for t in templates:
        if object["Class"]==t["class"]:
            return t

def getLink(obj1,obj2):
    link = {}
    class1 = getTemplate(obj1)
    class2 = getTemplate(obj2)
    #sort objects to and from
    if class2["component_types"] and obj1["Class"] in class2["component_types"]:
        obj1,obj2 = obj2,obj1
        class1,class2 = class2,class1
    #let's get the Link!
    links = obj1[class1["components"]]
    for l in links:
        found = True
        for i in range(0,len(class2["primary_keys"])-1):
            a=0
            field1 = class1["component_check_values"][i]
            field2 = class2["primary_keys"][i]
            if field1=="Component_name":
                if l[obj2["Class"]]!=obj2[field2]:
                    found = False
            elif l[field1]:
                if l[field1]!=obj2[field2]:
                    found = False
            else:
                if obj1[field1]!=obj2[field2]:
                    found = False
        if found == True:
            link = l
    return link

def parseRulesToString(object,rules):
    result = {}
    for rule in rules:
        if rules[rule][0] == "&":
            result[rule] = object[rules[rule].replace("&", "")]
        else:
            result[rule] = rules[rule]
    return result

def getOneClass(classname):
    list = []
    array = getAllObjects()
    for object in array:
        if(object["Class"]==classname):
            list.append(object)
    return list

def getDataFile(name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name) as data_file:
        data = json.load(data_file)
    return data