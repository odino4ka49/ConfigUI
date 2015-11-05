from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import json
import inspect, os


def index(request):
    template = loader.get_template('webvepp/index.html')
    return HttpResponse(template.render())

def loadTreeData(request):
    try:
        tree = parseTree("Chan_camacs")
    except Exception as e:
        print e
    return HttpResponse(json.dumps(tree, ensure_ascii=False), content_type="application/json")

def loadNodeNeighbours(request):
    try:
        data = request.GET
        node_id = data["node_id"]
        level = data["level"]
        node = getObjectById(node_id)
        n_list = getNodeNeighbours(node,level)
    except Exception as e:
        print e
    return HttpResponse(json.dumps(n_list, ensure_ascii=False), content_type="application/json")

#returns packed object
def parseObject(object):
    #if "link_id" in object:
        #result = {"name":object["Name"],"id":object["Name"],"link_id":object["link_id"],"_parents":[]}
    result = {"name":object["Name"],"id":object["Name"],"_parents":[]}
    """if "type" in object and object["type"]=="new":
        template = None
        sample = object"""
    template = getTemplate(object)
    obj_attributes = parseAttributes(template,object)
    result["attributes"]=obj_attributes
    if "components" in template and template["components"]:
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
            elif ("link_id" in object) and (type(field) is dict) and ("value" in field) and (field["value"]=="link_id"):
                attrs += [{
                        "key": field["key"],
                        "value": object["link_id"]
                    }]
            elif field in object:
                attrs += [{
                    "key": field,
                    "value": object[field]
                }]
        return attrs

    if("min" in template):
        attributes["min"] = parsing(template["min"])
        attributes["extra"] = parsing(template["max"])
    else:
        for field in template["fields"]:
            field_name = field["key"]
            attributes["min"] += [{
                "key": field_name,
                "value": object[field_name]
            }]
    return attributes

def getNodeNeighbours(node,level):
    neighbours = []
    sample = getSample("Chan_camacs")
    if level=="0":
        obj_sample = sample["root"]
    else:
        obj_sample = sample["level"+level]

    level_n = "level"+str(int(level)+1)
    if level_n in sample:
        sample_l = sample[level_n]
        if "type" in obj_sample and obj_sample["type"]=="new":
            next_level = getObjects(parseRulesToString(node,sample_l["filter"]))
            #for n in neighbours:
                #neighbours.append(parseObjectInfo(sample_l,n))
        else:
            next_level = getObjects(parseRulesToString(node,sample_l["filter"]))
            for n in next_level:
                link = getLink(n,node)
                if link != {}:
                    template = getTemplate(node)
                    if template["component_ID"]!=None:
                        n["link_id"] = link[template["component_ID"]]
                    neighbour = {"name":n["Name"],"id":"","_parents":[]}
                    if "Class" in n:
                        template = getTemplate(n)
                        pr_k = template["primary_keys"]
                        for key in pr_k:
                            neighbour["id"] += n[key]
                    display_details = sample_l["display_filter"]
                    print display_details
                    obj_attributes = parseAttributes(display_details,n)
                    neighbour["attributes"] = obj_attributes
                    neighbours.append(neighbour)
    return neighbours

def parseTree(name):
    tree = {}
    sample = getSample(name)
    max_level = 1

    def parseObjectInfo(obj_sample,object):
        result = {"name":object["Name"],"id":"","_parents":[]}
        if "Class" in object:
            template = getTemplate(object)
            pr_k = template["primary_keys"]
            for key in pr_k:
                result["id"] += object[key]
        if "type" in obj_sample and obj_sample["type"]=="new":
            result["id"] = object["Name"]
        display_details = obj_sample["display_filter"]
        obj_attributes = parseAttributes(display_details,object)
        result["attributes"]=obj_attributes

        level = "level"+str(obj_sample["level"]+1)
        if obj_sample["level"]<max_level and level in sample:
            sample_l = sample[level]
            if "type" in obj_sample and obj_sample["type"]=="new":
                neighbours = getObjects(parseRulesToString(object,sample_l["filter"]))
                for n in neighbours:
                    result["_parents"].append(parseObjectInfo(sample_l,n))
            else:
                neighbours = getObjects(parseRulesToString(object,sample_l["filter"]))
                for n in neighbours:
                    link = getLink(n,object)
                    #TODO: make it faster loading graph by parts
                    if link!= {}:
                        if template["component_ID"]!=None:
                            n["link_id"] = link[template["component_ID"]]
                        result["_parents"].append(parseObjectInfo(sample_l,n))
        return result

    def parseObjectNeighbours(object):
        None

    tree = parseObjectInfo(sample["root"],sample["root"]["fields"])
    parseObjectNeighbours(sample["root"])
    return tree

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

def getObjectById(id):
    object = {}
    data = getAllObjects()
    def filter(o):
        result = True
        o_id = ""
        template = getTemplate(o)
        if template:
            pr_k = template["primary_keys"]
            for key in pr_k:
                o_id += o[key]
        if o_id!= id:
            result = False
        return result
    for obj in data:
        if(filter(obj)):
            object = obj
    return object

def findObject(array,check_object,check_rules):
    result_object = {"Channels":[{"ID":8}]}
    for object in array:
        for check_field in check_rules:
            #if(object[check_field]==check_object[check_rules[check_field].replace("&", "")]):
                print "hohoh"
    return result_object

def getSample(name):
    samples = getDataFile("Chan_sample.json")
    return next((x for x in samples if x["name"] == name), None)

def getAllTemplates():
    return getDataFile("Chan_template.json")

def getAllObjects():
    return getDataFile("CHAN.json")

def getObjects(rules):
    objects = []
    data = getAllObjects()
    def filter(o):
        result = True
        for r in rules:
            if r in o and o[r]!=rules[r] and o[r] not in rules[r]:
                result = False
        return result
    for obj in data:
        if(filter(obj)):
            objects.append(obj)
    return objects

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
    elif class1["component_types"] and obj2["Class"] in class1["component_types"]:
        None
    else:
        if obj1["Class"] in obj2:
            obj1,obj2 = obj2,obj1
            class1,class2 = class2,class1
        elif obj2["Class"] in obj1:
            None
        else:
            return link
        found = True
        for i in range(0,len(class2["primary_keys"])-1):
            field2 = class2["primary_keys"][i]
            if field2=="Name":
                if obj1[obj2["Class"]]!=obj2[field2]:
                    found = False
            elif field2 in obj1:
                if obj1[field2]!=obj2[field2]:
                    found = False
            else:
                 found = False
        if found == True:
            link["Class"]=obj2["Name"]
        return link
    #let's get the Link!
    links = obj1[class1["components"]]
    for l in links:
        found = True
        for i in range(0,len(class2["primary_keys"])-1):
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