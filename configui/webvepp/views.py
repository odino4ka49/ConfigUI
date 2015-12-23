#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-15 -*-
# -*- coding: latin-1 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from sets import Set
from django.template import Context
import json
import inspect, os
import math
import copy

tree_data = {}
tree_template = {}
tree_sample = {}
tree_sample_name = ""
start_name = None
current_scheme_name = {"system":"CHAN","sample":"camacs"}

def index(request):
    global start_name
    template = loader.get_template('webvepp/index.html')
    start_name = None
    return HttpResponse(template.render())

def camacs(request,id=None):
    global start_name
    start_name = id
    template = loader.get_template('webvepp/index.html')
    return HttpResponse(template.render())

def elements(request,id=None):
    global start_name
    start_name = id
    template = loader.get_template('webvepp/index.html')
    return HttpResponse(template.render())

def loadTreeData(request):
    global start_name,current_scheme_name
    data = request.GET
    current_scheme_name = json.loads(data['scheme_names'])
    #try:
    tree = parseTree()
    if start_name:
        hideSiblings(tree["_parents"],start_name,1)
        for n in tree["_parents"]:
            if n["name"]==start_name:
                node = getObjectById(n["id"])
                n["_parents"] = getNodeNeighbours(node,"1")
                n["_children"] = getNodeNeighbours(node,"1",-1)
                tree["additional_links"] = getAdditionalLinks(n["_parents"],2)
    else:
        tree["additional_links"] = []
    #except Exception as e:
    #    print e
    return HttpResponse(json.dumps(tree, ensure_ascii=False), content_type="application/json")

def loadTreeSample(request):
    global current_scheme_name
    try:
        data = request.GET
        current_scheme_name = json.loads(data['scheme_names'])
        sample = getSample()
    except Exception as e:
        print e
    return HttpResponse(json.dumps(sample, ensure_ascii=False), content_type="application/json")

def loadNodeNeighbours(request):
    global current_scheme_name
    data = request.GET
    node_id = data["node_id"]
    level = data["level"]
    current_scheme_name = json.loads(data['scheme_names'])

    node = getObjectById(node_id)
    n_list = getNodeNeighbours(node,level)
    n_left_list = getNodeNeighbours(node,level,-1)
    r_list = getRemoteAttributes(node,level)
    l_list = getAdditionalLinks(n_list,int(level)+1)
    return HttpResponse(json.dumps([n_list,n_left_list,l_list,r_list], ensure_ascii=False), content_type="application/json")


def loadMaxAttributes(request):
    global current_scheme_name
    data = request.GET
    node_id = data["node_id"]
    level = data["level"]
    current_scheme_name = json.loads(data['scheme_names'])

    node = getObjectById(node_id)
    attributes = getMaxAttributes(node,level)
    return HttpResponse(json.dumps(attributes, ensure_ascii=False), content_type="application/json")

#returns packed object
def parseObject(object):
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
def parseAttributes(template,object,attr_type="min"):
    attributes = {"min":[],"extra":[]}
    def parsing(field_list):
        attrs = []
        for field in field_list:
            if (type(field) is dict) and ('link_to' in field) and ('link_from' in field):
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
                objs2 = getObjects(rules)
                for obj2 in objs2:
                    link = getLink(object,obj2)
                    if link:
                        attrs += [{
                            "key": field["key"],
                            "value": link[field["value"]]
                        }]
            elif (type(field) is dict) and (field["value"][0]=="&"):
                value = getValueByPath(object,field["value"])
                attrs += [{
                    "key": field["key"],
                    "value": value
                }]
            elif (type(field) is dict) and ("to_array" in field):
                field_array = getValuesByPath(object,field["to_array"]["Path"])
                if field["to_array"]["Operation"]=="sum":
                    sum = 0
                    for val in field_array:
                        sum+=val
                    if sum!=0:
                        attrs += [{
                            "key": field["key"],
                            "value": sum
                        }]
            elif ("link_id" in object) and (type(field) is dict) and ("value" in field) and (field["value"]=="link_id"):
                attrs += [{
                        "key": field["key"],
                        "value": object["link_id"]
                    }]
            elif field=="*":
                for key in object:
                    attrs += [{
                        "key": key,
                        "value": object[key]
                    }]
            elif (field in object) and (type(object[field]) is list):
                attrs += [{
                    "key": field,
                    "value": len(object[field])
                }]
            elif field in object:
                attrs += [{
                    "key": field,
                    "value": object[field]
                }]
        return attrs

    def check_unique(attrs):
        for attr in attrs["min"]:
            if attr in attrs["extra"]:
                attrs["extra"].remove(attr)
        return attrs

    if(attr_type in template):
        if(attr_type=="max"):
            attributes["extra"] = parsing(template["max"])
        else:
            attributes[attr_type] = parsing(template[attr_type])
        #attributes["extra"] = parsing(template["max"])
        """elif(attr_type=="remote"):
        attributes = parsing(template)
        print object"""
    else:
        for field in template["fields"]:
            field_name = field["key"]
            attributes["min"] += [{
                "key": field_name,
                "value": object[field_name]
            }]
    return attributes

def getMaxAttributes(node,level):
    sample = getSample()
    sample_l = sample["level"+level]
    display_details = sample_l["display_filter"]
    obj_attributes = parseAttributes(display_details,node,"max")
    return obj_attributes["extra"]

def getNodeNeighbours(node,level,direction=1):
    neighbours = []
    sample = getSample()
    if level=="0":
        obj_sample = sample["root"]
    else:
        obj_sample = sample["level"+level]

    if direction==-1:
        if level=="1":
            level_n = "level-1"
        elif int(level)<0:
            level_n = "level"+str(int(level)-1)
        else:
            return neighbours
    else:
        level_n = "level"+str(int(level)+1)
    if level_n in sample:
        sample_l = sample[level_n]
        next_level = getObjects(parseRulesToString(node,sample_l["filter"]))
        if "type" in obj_sample and obj_sample["type"]=="new":
            for n in next_level:
                neighbour = {"name":n["Name"],"id":"","_parents":[]}
                if "Class" in n:
                    neighbour["id"] = parseId(n)
                display_details = sample_l["display_filter"]
                obj_attributes = parseAttributes(display_details,n)
                neighbour["attributes"] = obj_attributes
                n_display_attributes = sample_l["display_attributes"]
                neighbour["width"] = n_display_attributes["width"]
                neighbour["height"] = n_display_attributes["height"]
                neighbour["direction"] = direction
                neighbours.append(neighbour)
        else:
            for n in next_level:
                link = getLink(n,node)
                if link != {}:
                    template = getTemplate(node)
                    if template["component_ID"]!=None:
                        n["link_id"] = link[template["component_ID"]]
                    neighbour = {"name":n["Name"],"id":"","_parents":[]}
                    if "Class" in n:
                        neighbour["id"] = parseId(n)
                    display_details = sample_l["display_filter"]
                    obj_attributes = parseAttributes(display_details,n)
                    neighbour["attributes"] = obj_attributes
                    n_display_attributes = sample_l["display_attributes"]
                    neighbour["width"] = n_display_attributes["width"]
                    neighbour["height"] = n_display_attributes["height"]
                    neighbour["direction"] = direction
                    if "action" in sample_l:
                        action = parseRulesToString(n,sample_l["action"])
                        if action["type"]=="open_another_map" and "info" in action:
                            neighbour["link_to_map"] = action["map"]+"/"+action["info"]
                    if "autorevealing" in n_display_attributes and n_display_attributes["autorevealing"]:
                        neighbour["_parents"]=getNodeNeighbours(n,str(int(level)+1))
                    neighbours.append(neighbour)
        #if we have a matrix neighbours, we add some kind of "matrix" object in the beginning of all neighbours
        if "positioning" in sample_l["display_attributes"] and sample_l["display_attributes"]["positioning"]=="matrix":
            #create matrix element with all needed stuff
            matrix = {"name":"Matrix","id":parseId(node)+"matrix","_parents":[],"attributes":{"min":[],"extra":[]},"direction":direction}
            #load matrix size and then count all matrix sizes
            matrix_size = sample_l["display_attributes"]["matrix_size"]
            if type(matrix_size) is unicode and matrix_size[0]=="&":
                matrix_size = getValueByPath(node,matrix_size)
            if matrix_size==None:
                matrix_size = len(neighbours)
            if matrix_size!=0:
                matrix_cols = 8 if matrix_size > 16 else 4#math.ceil(math.sqrt(matrix_size))
                matrix_rows = math.ceil(float(matrix_size)/matrix_cols)
                matrix["cols"]=matrix_cols
                matrix["rows"]=matrix_rows
                matrix["width"]=(sample_l["display_attributes"]["width"]+20)*matrix_cols
                matrix["height"]=(sample_l["display_attributes"]["height"]+10)*matrix_rows
                if "sort_field" in sample_l:
                    if sample_l["display_attributes"]["matrix_type"]=="channels":
                        neighbours = sortMatrixObjects(neighbours,sample_l["sort_field"],matrix_size,node)
                    else:
                        neighbours = sorted(neighbours, key=lambda k: next((attr for attr in k["attributes"]["min"] if attr["key"]==sample_l["sort_field"]),{"value":""})["value"])
                #append it to neighbours
                neighbours.append(matrix)
        elif "sort_field" in sample_l:
            neighbours = sorted(neighbours, key=lambda k: next((attr for attr in k["attributes"]["min"] if attr["key"]==sample_l["sort_field"]),{"value":""})["value"])
    return neighbours

def getRemoteAttributes(node,level):
    remote = {}
    sample = getSample()
    obj_sample = {}
    if level=="0":
        return None
    else:
        obj_sample = sample["level"+level]
    if "remote_attributes" in obj_sample and "Class" in obj_sample["remote_attributes"] and node["Class"] in obj_sample["remote_attributes"]["Class"]:
        attribute_names = obj_sample["remote_attributes"]["attributes"]
        obj_attributes = []
        for attr in attribute_names:
            if attr == "variables":
                if node["Inputs"]==2:
                    obj_attributes.append(["X","Y"])
                elif node["Inputs"]==1:
                    obj_attributes.append(["X"])
            else:
                obj_attributes.append(getValueByPath(node,attr))
        remote["attributes"]=obj_attributes
        remote["type"] = obj_sample["remote_attributes"]["type"]
        if remote["type"]=="matrix_equation":
            vector1 = countMatrixWidthHeight(obj_attributes[0])
            vector2 = countMatrixWidthHeight(obj_attributes[2])
            matrix1 = countMatrixWidthHeight(obj_attributes[1])
            matrix2 = countMatrixWidthHeight(obj_attributes[4])
            remote["width"] = (vector1["width"]+vector2["width"]+max(matrix1["width"],matrix2["width"])+8)*8+10
            remote["height"] = (max(vector1["height"],vector2["height"],matrix1["height"])+max(vector1["height"],vector2["height"],matrix2["height"])+5)*11+5
    else:
        return None
    return remote

def countMatrixWidthHeight(matrix):
    width = 0
    height = len(matrix)
    matrixtype = "matrix" if type(matrix[0]) is list else "vector"
    for row in matrix:
        if matrixtype=="vector":
            width = max(width,len(str(row)))
        elif matrixtype=="matrix":
            row_width = 0
            for item in row:
                row_width += len(str(item))+1
            width = max(width,row_width)
    return {"width": width,"height": height}

def sortMatrixObjects(objects,sortname,size,parent_node):
    sorted = []
    def findObject(number):
        for obj in objects:
            for field in obj["attributes"]["min"]:
                if field["key"]==sortname:
                    if field["value"]==number:
                        field["key"]="Index"
                        return obj
                    elif field["value"]==None:
                        field["key"]="Index"
                        field["value"]=number
                        return obj
                    elif type(field["value"]) is list and number in field["value"]:
                        object = copy.deepcopy(obj)
                        object["id"]+=str(number)
                        for f in object["attributes"]["min"]:
                            if f["key"]==sortname:
                                f["key"]="Index"
                                f["value"]=number
                        return object
        return None

    for i in range(0,size):
        object = findObject(i)
        if object!=None:
            sorted.append(object)
        else:
            object = {"name":"Matrix","id":parseId(parent_node)+str(i),"_parents":[],"attributes":{"min":[{"key":"Index","value":i}],"extra":[]},"width":50,"height":50}
            sorted.append(object)
    return sorted

def getAdditionalLinks(nodes,level):
    add_links = []
    sample = getSample()
    if level==0:
        return add_links
    else:
        level_n = "level"+str(level)
        if level_n not in sample:
            return add_links
        sample_l = sample[level_n]
        if "additional_links" in sample_l:
            for add_link in sample_l["additional_links"]:
                links_class = getOneClass(add_link)
                for lc in links_class:
                    for n in nodes:
                        if lc["Name"]==n["name"]:
                            template = getTemplate(lc)
                            if template["components"]!= None:
                                lc_links = lc[template["components"]]
                                for to_obj in lc_links:
                                    rules = {}
                                    for key in to_obj:
                                        if key in template["component_types"]:
                                            rules = {"Class":key,"Name":to_obj[key],"System":lc["System"]}
                                    to_object = getObject(rules)
                                    to_id = parseId(to_object)
                                    add_links.append({"from":n["id"],"to":to_id,"id":n["id"]+to_id,"text":to_obj[template["component_ID"]]})
        level_info = sample_l["display_attributes"]
        if "autorevealing" in level_info and level_info["autorevealing"]:
            #get thelist of id's
            uniq_ids = Set([])
            for n in nodes:
                for nl in n["_parents"]:
                    if nl["id"] in uniq_ids:
                        n["_parents"]=[]
                        add_links.append({"from":nl["id"],"to":n["id"],"id":nl["id"]+n["id"],"text":""})
                    else:
                        uniq_ids.add(nl["id"])
            #walk through nextlevel
            #if there are same id's
            #create additional link and remove _parent
    return add_links

def hideSiblings(neighbours,start_name,level):
    #hide siblings
    if len(neighbours)==0:
        return
    sample = getSample()
    level_n = "level"+str(level)
    sample_l = sample[level_n]
    level_info = sample_l["display_attributes"]
    if "hiding" not in level_info or level_info["hiding"]==False:
        return
    for n in neighbours:
        if n["name"]!=start_name:
            n["hidden"] = True
        else:
            n["unhidden"] = True
    return

def parseTree():
    tree = {}
    sample = getSample()
    max_level = 1

    def parseObjectInfo(obj_sample,object):
        result = {"name":object["Name"],"id":"","_parents":[]}
        if "Class" in object:
            result["id"] = parseId(object)
        if "type" in obj_sample and obj_sample["type"]=="new":
            result["id"] = object["Name"]
        display_details = obj_sample["display_filter"]
        obj_attributes = parseAttributes(display_details,object)
        result["attributes"]=obj_attributes
        obj_display_attributes = obj_sample["display_attributes"]
        result["width"] = obj_display_attributes["width"]
        result["height"] = obj_display_attributes["height"]

        result["_parents"]=getNodeNeighbours(result,"0")
        """level = "level"+str(obj_sample["level"]+1)
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
                        result["_parents"].append(parseObjectInfo(sample_l,n))"""
        return result

    if sample["root"]["type"]=="new":
        tree = parseObjectInfo(sample["root"],sample["root"]["fields"])
    return tree

def getValuesByPath(object,path):
    values = [object]
    #split path
    path = path.replace("&", "").split("->")

    def getObjectInChain(object,step):
        template = getClassTemplate(object["Class"])
        next = []
        if step==template["components"]:
            for comp in object[step]:
                for key in comp:
                    if key in template["component_types"]:
                        rules = {"Class":key,"Name":comp[key],"System":object["System"]}
                next += getObjects(rules)
        else:
            next.append(getNeighbour(object,step))
        return next
    #loop where we go through path and change current value (it might be an object if it's not the end of the path)
    for i in range(0,len(path)-1):
        next_vals = []
        for obj in values:
            next_vals += getObjectInChain(obj,path[i])
        values = next_vals
    next_vals = []
    for value in values:
        if value and path[-1] in value:
            next_vals.append(value[path[-1]])
    return next_vals

def getValueByPath(object,path):
    value = object
    #split path
    path = path.replace("&", "").split("->")
    #loop where we go through path and change current value (it might be an object if it's not the end of the path)
    for i in range(0,len(path)-1):
        value = getNeighbour(value,path[i])
    if value and path[-1] in value:
        value = value[path[-1]]
    return value

def getNeighbour(object,foreign_key):
    neighbour = None
    if foreign_key in object:
        #create rules
        rules = {"Class":foreign_key,"Name":object[foreign_key],"System":object["System"]}
        #get object
        neighbour = getObject(rules)
    else:
        rules = {"Class":foreign_key,"System":object["System"]}
        neighbours = getObjects(rules)
        link = {}
        for n in neighbours:
            link = getLink(object,n)
            if link!={}:
                neighbour = n
    return neighbour

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

def parseId(object):
    if "Class" not in object:
        return object["name"]
    id = object["Class"]
    template = getTemplate(object)
    if template:
        pr_k = template["primary_keys"]
        for key in pr_k:
            id+=object[key]
    return id

def getObjectById(id):
    object = {}
    id_way = id.split("->")
    id = id_way[len(id_way)-1]
    data = getAllObjects()
    def filter(o):
        result = True
        o_id=parseId(o)
        if o_id!= id:
            result = False
        return result
    for obj in data:
        if(filter(obj)):
            object = obj
    return object

def getSample():
    global tree_sample,current_scheme_name
    system_name = current_scheme_name["system"]
    sample_name = current_scheme_name["sample"]
    tree_sample_name = "Chan_camacs"
    if sample_name == "elements":
        tree_sample_name = "Chan_elements"
    if system_name not in tree_sample:
        if system_name == "CHAN":
            tree_sample[system_name] = getDataFile("Chan_sample.json")
        else:
            tree_sample[system_name] = []
    samples = tree_sample[system_name]
    return next((x for x in samples if x["name"] == tree_sample_name), None)

def getAllTemplates():
    global tree_template,current_scheme_name
    system_name = current_scheme_name["system"]
    if system_name not in tree_template:
        if system_name == "CHAN":
            tree_template[system_name] = getDataFile("Chan_template.json")
        else:
            tree_template[system_name] = []
    return tree_template[system_name]

def getAllObjects():
    global tree_data,current_scheme_name
    system_name = current_scheme_name["system"]
    if system_name not in tree_data:
        if system_name == "CHAN":
            tree_data[system_name] = getDataFile("CHAN.json")
        else:
            tree_data[system_name] = []
    return tree_data[system_name]

def getObjects(rules):
    objects = []
    data = getAllObjects()
    def filter(o):
        result = True
        for r in rules:
            if rules[r]==None:
                result = False
            elif type(rules[r]) is unicode:
                if r in o and o[r]!=rules[r]:
                    result = False
            elif type(rules[r]) is list:
                if r in o and o[r] not in rules[r]:
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

    def checkForLinkLike(obj1,obj2,class1,class2):
        link = {}
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

    #sort objects to and from
    if class2["component_types"] and obj1["Class"] in class2["component_types"]:
        obj1,obj2 = obj2,obj1
        class1,class2 = class2,class1
    elif class1["component_types"] and obj2["Class"] in class1["component_types"]:
        None
    else:
    #check for linklike (not in components) connection
        return checkForLinkLike(obj1,obj2,class1,class2)
    #let's get the Link!
    links = obj1[class1["components"]]
    for l in links:
        found = True
        for i in range(0,len(class2["primary_keys"])-1):
            field1 = class1["component_check_values"][i]
            field2 = class2["primary_keys"][i]
            if field1=="Component_name":
                if obj2["Class"] in l:
                    if l[obj2["Class"]]!=obj2[field2]:
                        found = False
                else:
                    found = False
            elif field1 in l and l[field1]:
                if l[field1]!=obj2[field2]:
                    found = False
            else:
                if obj1[field1]!=obj2[field2]:
                    found = False
        if found == True:
            link = l
    if link=={}:
        return checkForLinkLike(obj1,obj2,class1,class2)
    return link

def parseRulesToString(object,rules):
    result = {}
    for rule in rules:
        if rules[rule][0] == "&":
            new_rule = rules[rule].replace("&", "")
            if new_rule in object:
                result[rule] = object[new_rule]
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