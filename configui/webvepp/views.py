from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
import json
import inspect, os
import math
import copy

tree_data = []
tree_template = []
tree_sample = []
tree_sample_name = ""

def index(request):
    global tree_data, tree_sample, tree_template,tree_sample_name
    template = loader.get_template('webvepp/index.html')
    tree_data = getDataFile("CHAN.json")
    tree_template = getDataFile("Chan_template.json")
    tree_sample = getDataFile("Chan_sample.json")
    tree_sample_name = "Chan_camacs"
    return HttpResponse(template.render())

def elements(request):
    global tree_data, tree_sample, tree_template,tree_sample_name
    template = loader.get_template('webvepp/index.html')
    tree_data = getDataFile("CHAN.json")
    tree_template = getDataFile("Chan_template.json")
    tree_sample = getDataFile("Chan_sample.json")
    tree_sample_name = "Chan_elements"
    return HttpResponse(template.render())

def loadTreeData(request):
    try:
        tree = parseTree()
        tree["additional_links"] = []
    except Exception as e:
        print e
    return HttpResponse(json.dumps(tree, ensure_ascii=False), content_type="application/json")

def loadTreeSample(request):
    try:
        sample = getSample()
    except Exception as e:
        print e
    return HttpResponse(json.dumps(sample, ensure_ascii=False), content_type="application/json")

def loadNodeNeighbours(request):
    #try:
    data = request.GET
    node_id = data["node_id"]
    level = data["level"]
    node = getObjectById(node_id)
    n_list = getNodeNeighbours(node,level)
    l_list = getAdditionalLinks(n_list,int(level)+1)
    """except Exception as e:
        print e"""
    return HttpResponse(json.dumps([n_list,l_list], ensure_ascii=False), content_type="application/json")

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
def parseAttributes(template,object):
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
    sample = getSample()
    if level=="0":
        obj_sample = sample["root"]
    else:
        obj_sample = sample["level"+level]

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
                    neighbours.append(neighbour)
        #if we have a matrix neighbours, we add some kind of "matrix" object in the beginning of all neighbours
        if "positioning" in sample_l["display_attributes"] and sample_l["display_attributes"]["positioning"]=="matrix":
            #create matrix element with all needed stuff
            matrix = {"name":"Matrix","id":parseId(node)+"matrix","_parents":[],"attributes":{"min":[],"extra":[]}}
            #load matrix size and then count all matrix sizes
            matrix_size = sample_l["display_attributes"]["matrix_size"]
            if type(matrix_size) is unicode and matrix_size[0]=="&":
                matrix_size = getValueByPath(node,matrix_size)
            if matrix_size:
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

def sortMatrixObjects(objects,sortname,size,parent_node):
    sorted = []
    def findObject(number):
        for obj in objects:
            for field in obj["attributes"]["min"]:
                if field["key"]==sortname:
                    if field["value"]==number:
                        field["key"]="Index"
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
    return add_links


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

def getValueByPath(object,path):
    value = object
    #split path
    path = path.replace("&", "").split("->")
    #loop where we go through path and change current value (it might be an object if it's not the end of the path)
    for i in range(0,len(path)-1):
        value = getNeighbour(value,path[i])
    if path[-1] in value:
        value = value[path[-1]]
    return value

def getNeighbour(object,foreign_key):
    neighbour = None
    #create rules
    rules = {"Class":foreign_key,"Name":object[foreign_key],"System":object["System"]}
    #get object
    neighbour = getObject(rules)
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
    global tree_sample,tree_sample_name
    samples = tree_sample#getDataFile("Chan_sample.json")
    return next((x for x in samples if x["name"] == tree_sample_name), None)

def getAllTemplates():
    global tree_template
    return tree_template#getDataFile("Chan_template.json")

def getAllObjects():
    global tree_data
    return tree_data#getDataFile("CHAN.json")

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