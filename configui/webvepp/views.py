#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-15 -*-
# -*- coding: latin-1 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from sets import Set
from xml.dom import minidom
from django.template import Context
import json
import inspect, os
import math
import copy
import re
import validation

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

def tools(request):
    template = loader.get_template('webvepp/tools.html')
    return HttpResponse(template.render())

def settings(request):
    template = loader.get_template('webvepp/settings.html')
    return HttpResponse(template.render())

def scheme(request):
    template = loader.get_template('webvepp/scheme.html')
    return HttpResponse(template.render())

def findObject(request):
    global start_name,current_scheme_name
    data = request.GET
    current_scheme_name = json.loads(data['scheme_names'])
    start_name = json.loads(data['start_name'])
    result = {"reload": "true","tree":[]}
    rules = {"Name": start_name}
    start_obj = getObjects(rules)
    if len(start_obj) != 0:
        result["reload"] = "false"
        tree_filter_data = searchTreeThrough(start_obj[0])
        result["filter_name"] = tree_filter_data["filter_name"]
        #result["tree"] = tree_filter_data["tree"]
        #result["path"] = tree_filter_data["path"]
    return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

def loadTreeData(request):
    global current_scheme_name
    data = request.GET
    current_scheme_name = json.loads(data['scheme_names'])
    filter_name = json.loads(data['filter_name'])
    rules = getFilter(filter_name)
    tree = parseTree(rules)
    tree["additional_links"] = []
    return HttpResponse(json.dumps(tree, ensure_ascii=False), content_type="application/json")

def loadListData(request):
    global current_scheme_name
    data = request.GET
    current_scheme_name = json.loads(data['scheme_names'])
    list = parseList()
    return HttpResponse(json.dumps(list, ensure_ascii=False), content_type="application/json")

def loadToolData(request):
    try:
        data = request.GET
        system_name = json.loads(data['system_name'])
        tool_data = getTools(system_name)
    except Exception as e:
        print e
    return HttpResponse(json.dumps(tool_data, ensure_ascii=False), content_type="application/json")

def loadMenuData(request):
    try:
        data = request.GET
        system_name = json.loads(data['system_name'])
        menu_data = getMenu(system_name)
    except Exception as e:
        print e
    return HttpResponse(json.dumps(menu_data, ensure_ascii=False), content_type="application/json")

def loadValidationData(request):
    data = request.GET
    scheme_names = json.loads(data["scheme_names"])
    validation.setSystemName(scheme_names["system"])
    validation_log = validation.getValidationLog()
    return HttpResponse(json.dumps(validation_log, ensure_ascii=False), content_type="application/json")

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
"""def parseObject(object):
    result = {"name":object["Name"],"id":object["Name"],"_parents":[]}

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
            for i in range(0,len(comp_temp["primary_key"])-1):
                field1 = template["component_check_values"][i]
                field2 = comp_temp["primary_key"][i]
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
    return result"""

#returns list of attributes of the object according to its template
def parseAttributes(desplay_det,object,attr_type="min"):
    attributes = {"min":[],"extra":[]}
    def parsing(field_list):
        template = getTemplate(object)
        attrs = []
        for field in field_list:
            if (type(field) is dict):
                if ('link_to' in field) and ('link_from' in field):
                    obj1 = getObject(parseRulesToString(object,field['link_from']))
                    obj2 = getObject(parseRulesToString(object,field['link_to']))
                    if obj2 and obj1:
                        links = getLink(obj1,obj2,{})
                        if(len(links)>0):
                            attrs += [{
                                "key": field["key"],
                                "value": links[0][field["value"]]
                            }]
                elif ('link_to' in field):
                    #if we do this channels->id thing
                    rules = parseRulesToString(object,field['link_to'])
                    objs2 = getObjects(rules)
                    for obj2 in objs2:
                        links = getLink(object,obj2,{})
                        if len(links)>0:
                            attrs += [{
                                "key": field["key"],
                                "value": links[0][field["value"]]
                            }]
                elif (field["value"]=="len"):
                    if field["key"] in object:
                        attrs += [{
                            "key": field["key"],
                            "value": len(object[field["key"]])
                        }]
                elif (field["value"][0]=="&"):
                    value = getValuesByPath(object,field["value"])
                    if value!=None:
                        attrs += [{
                            "key": field["key"],
                            "value": value
                        }]
                elif ("to_array" in field):
                    field_array = getValuesByPath(object,field["to_array"]["Path"])
                    if field["to_array"]["Operation"]=="sum":
                        sum = 0.0
                        for val in field_array:
                            sum+=val
                        if sum!=0:
                            attrs += [{
                                "key": field["key"],
                                "value": round(sum,1)
                            }]
                elif ("link_id" in object)and ("value" in field) and (field["value"]=="link_id"):
                    if "positioning" in field and field["positioning"]=="link_text":
                        #if len(object["link_id"])==2:
                        attrs += [{
                            "key": field["key"],
                            "value": object["link_id"]["from"],
                            "link_end_id": object["link_id"]["to"],
                            "positioning": field["positioning"]
                        }]
                    else:
                        attrs += [{
                            "key": field["key"],
                            "value": object["link_id"]["from"]
                        }]
                elif field["value"] in object:
                    attrs += [{
                        "key": field["key"],
                        "value": object[field["value"]]
                    }]
                if "type" in field:
                    if field["type"]=="len":
                        attr = next((x for x in attrs if x["key"] == field["key"]), {})
                        if attr and type(attr["value"]) is list:
                            attr["value"] = len(attr["value"])
            else:
                temp_field = {}
                if field=="*":
                    for key in object:
                        if template:
                            temp_field = next((x for x in template["fields"] if x["key"] == key), {})
                        if "units" in temp_field:
                            units = " "+str(temp_field["units"])
                            attrs += [{
                                "key": key,
                                "value": unicode(object[key])+units
                            }]
                        else:
                            attrs += [{
                                "key": key,
                                "value": object[key]
                            }]
                elif field in object:
                    if template:
                        temp_field = next((x for x in template["fields"] if x["key"] == field), {})
                    if "units" in temp_field:
                        units = " "+str(temp_field["units"])
                        attrs += [{
                            "key": field,
                            "value": unicode(object[field])+units
                        }]
                    else:
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

    if(attr_type in desplay_det):
        if(attr_type=="max"):
            attributes["extra"] = parsing(desplay_det["max"])
        else:
            attributes[attr_type] = parsing(desplay_det[attr_type])
        #attributes["extra"] = parsing(template["max"])
        """elif(attr_type=="remote"):
        attributes = parsing(template)
        print object"""
    else:
        for field in desplay_det["fields"]:
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

def getNodeNeighbours(node,level,direction=1,rules=None):
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
        if("type" in sample_l and sample_l["type"]=="new"):
            next_level = [
                sample_l["fields"]
            ]
        else:
            next_level = getObjects(parseRulesToString(node,sample_l["filter"]))
        #let's filter if there's some additional filter as 'rules'
        if rules:
            next_level = filterObjects(next_level,rules)
        if "type" in obj_sample and obj_sample["type"]=="new":
            for n in next_level:
                neighbour = {"name":n["Name"],"id":"","_parents":[]}
                if "Class" in n:
                    neighbour["id"] = parseId(n)
                if "Disabled" in n:
                    neighbour["disabled"] = n["Disabled"]
                display_details = sample_l["display_filter"]
                obj_attributes = parseAttributes(display_details,n)
                neighbour["attributes"] = obj_attributes
                n_display_attributes = sample_l["display_attributes"]
                neighbour["width"] = n_display_attributes["width"]
                neighbour["height"] = n_display_attributes["height"]
                neighbour["direction"] = direction
                if "remote_attributes" in sample_l and "Class" in sample_l["remote_attributes"] and n["Class"] in sample_l["remote_attributes"]["Class"]:
                    if "open_extra" in sample_l["remote_attributes"]:
                        neighbour["open_extra"] = sample_l["remote_attributes"]["open_extra"]
                if "autorevealing" in n_display_attributes and n_display_attributes["autorevealing"]:
                    neighbour["collapsed"]=False
                    neighbour["_parents"]=getNodeNeighbours(n,str(int(level)+1))
                neighbours.append(neighbour)
        else:
            for n in next_level:
                link_positions = {}
                links = getLink(node,n,link_positions)
                if len(links)!=0:
                    template = getTemplate(node)
                    n["link_id"] = link_positions
                    neighbour = {"name":n["Name"],"id":"","_parents":[]}
                    if "Class" in n:
                        neighbour["id"] = parseId(n)
                    if "Disabled" in n:
                        neighbour["disabled"] = n["Disabled"]
                    display_details = sample_l["display_filter"]
                    obj_attributes = parseAttributes(display_details,n)
                    neighbour["attributes"] = obj_attributes
                    n_display_attributes = sample_l["display_attributes"]
                    neighbour["width"] = n_display_attributes["width"]
                    neighbour["height"] = n_display_attributes["height"]
                    neighbour["direction"] = direction
                    if "remote_attributes" in sample_l and "Class" in sample_l["remote_attributes"] and neighbour["Class"] in sample_l["remote_attributes"]["Class"]:
                        if "open_extra" in sample_l["remote_attributes"]:
                            neighbour["open_extra"] = sample_l["remote_attributes"]["open_extra"]
                    if "action" in sample_l:
                        action = parseRulesToString(n,sample_l["action"])
                        if action["type"]=="open_another_map" and "info" in action:
                            neighbour["link_to_map"] = action["map"]+"/"+action["info"]
                    if "autorevealing" in n_display_attributes and n_display_attributes["autorevealing"]:
                        neighbour["collapsed"]=False
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
                if "matrix_cols" in sample_l["display_attributes"]:
                    matrix_cols = sample_l["display_attributes"]["matrix_cols"]
                else:
                    matrix_cols = 8 if matrix_size > 16 else 4#math.ceil(math.sqrt(matrix_size))
                matrix_rows = math.ceil(float(matrix_size)/matrix_cols)
                matrix["cols"]=matrix_cols
                matrix["rows"]=matrix_rows
                matrix["width"]=(sample_l["display_attributes"]["width"]+20)*matrix_cols
                matrix["height"]=(sample_l["display_attributes"]["height"]+10)*matrix_rows
                matrix["matrix"]=True
                if "sort_field" in sample_l:
                    sortfields = []
                    if isinstance(sample_l["sort_field"],basestring):
                        sortfields.append(sample_l["sort_field"])
                    elif type(sample_l["sort_field"]) is list:
                        sortfields = sample_l["sort_field"]
                    if sample_l["display_attributes"]["matrix_type"]=="channels":
                        for sortfield in sortfields:
                            neighbours = sortMatrixObjects(neighbours,sortfield,matrix_size,node)
                    else:
                        for sortfield in sortfields:
                            neighbours = sorted(neighbours, key=lambda k: next((attr for attr in k["attributes"]["min"] if attr["key"]==sortfield),{"value":""})["value"])
                #append it to neighbours
                neighbours.insert(0,matrix)
        elif "sort_field" in sample_l:
            sortfields = []
            if isinstance(sample_l["sort_field"],basestring):
                sortfields.append(sample_l["sort_field"])
            elif type(sample_l["sort_field"]) is list:
                sortfields = sample_l["sort_field"]
            for sortfield in sortfields:
                neighbours = sorted(neighbours, key=lambda k: next((attr for attr in k["attributes"]["min"] if attr["key"]==sortfield),{"value":""})["value"])
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
        if "open_extra" in obj_sample["remote_attributes"] and obj_sample["remote_attributes"]["open_extra"]=="true":
            node["open_extra"] = "true"
        attribute_names = obj_sample["remote_attributes"]["attributes"]
        obj_attributes = []
        for attr in attribute_names:
            if attr == "variables":
                if node["Outputs"]==2:
                    obj_attributes.append(["Out1","Out2"])
                elif node["Outputs"]==1:
                    obj_attributes.append(["Out1"])
            #wanted to reverse matrix here
            elif attr == "Graphs":
                m = getValueByPath(node,attr)
                obj_attributes.append(reverseMatrix(normalizeMatrix(getValueByPath(node,attr),node["Inputs"],node["Outputs"])))
            else:
                obj_attributes.append(reverseMatrix(normalizeMatrix(getValueByPath(node,attr),node["Inputs"],node["Outputs"])))
        remote["attributes"]=obj_attributes
        if node["Outputs"]==1 and node["Inputs"]==1:
            remote["noborders"] = True
        remote["type"] = obj_sample["remote_attributes"]["type"]
        if remote["type"]=="matrix_equation":
            vector1 = countMatrixWidthHeight(obj_attributes[0])
            vector2 = countMatrixWidthHeight(obj_attributes[2])
            vector3 = countMatrixWidthHeight(obj_attributes[7])
            matrix1 = countMatrixWidthHeight(obj_attributes[1])
            matrix2 = countMatrixWidthHeightReversed(obj_attributes[4])
            remote["width"] = (vector1["width"]+vector2["width"]+max(matrix1["width"],matrix2["width"])+8)*9+30
            remote["height"] = (max(vector1["height"],vector2["height"],matrix1["height"])+max(vector1["height"],vector2["height"],matrix2["height"])+max(vector3["height"],vector2["height"])+5)*17+20
    else:
        return None
    return remote

def reverseMatrix(matrix):
    if matrix==None or len(matrix)==0:
        return matrix
    matrixtype = "matrix" if type(matrix[0]) is list else "vector"
    if matrixtype=="vector":
        return matrix
    result = [[] for x in range(len(matrix[0]))]
    for row in matrix:
        for i in range(0,len(row)):
            result[i].append(row[i])
    return result

def normalizeMatrix(matrix,inputs,outputs):
    if matrix==None or len(matrix)==0:
        return matrix
    result = []
    matrixtype = "matrix" if type(matrix[0]) is list else "vector"
    if outputs == 1:
        if matrixtype == "matrix":
            for row in matrix:
                item_to_add = 0
                for item in row:
                    if item!=0:
                        item_to_add = item
                        break
                result.append([item_to_add])
            matrix = result
            if not type(matrix[0]) is list:
                matrixtype = "vector"
    for i in range(0,inputs):
        if len(matrix)-1>=i:
            if matrixtype=="matrix":
                line = matrix[i]
                if len(line)<outputs:
                    line.append([0]*(outputs-len(line)))
        else:
            if matrixtype=="vector":
                matrix.append(0)
            else:
                matrix.append([0]*outputs)
    if result == []:
        return matrix
    return result

def countMatrixWidthHeight(matrix):
    if matrix==None:
        return {"width": 1,"height": 1}
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

def countMatrixWidthHeightReversed(matrix):
    if matrix==None:
        return {"width": 1,"height": 1}
    matrixtype = "matrix" if type(matrix[0]) is list else "vector"
    if matrixtype=="vector":
        height = 1
    else:
        height = len(matrix[0])
    width = len(matrix)
    for row in matrix:
        item_width = 0
        if matrixtype=="vector":
            item_width = len(str(row))+1
        else:
            for item in row:
                item_width = max(item_width,len(str(item))+1)
        width+=item_width
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
            width = 50
            height = 50
            if len(objects)!=0:
                width = objects[0]["width"]
                height = objects[0]["height"]
            object = {"name":"Matrix","id":parseId(parent_node)+str(i),"_parents":[],"attributes":{"min":[{"key":"Index","value":i}],"extra":[]},"width":width,"height":height}
            sorted.append(object)
    return sorted

def listFillGaps(list,sortname):
    sorted = []
    index = 1
    for obj in list:
        attrs = obj["attributes"]["min"]
        sortfield = next((x for x in attrs if x["key"]==sortname),None)
        if sortfield!=None and sortfield["value"]!=None:
            if sortfield["value"]-index==1:
                index+=1
            elif sortfield["value"]-index>1:
                for i in range(index+1,sortfield["value"]):
                    gap_obj = {"id":i,"attributes":{"min":[{"key":sortname,"value":i}],"extra":[]}}
                    sorted.append(gap_obj)
                index=sortfield["value"]
            sorted.append(obj)
    return sorted

def listNumbering(list):
    index = 1
    for obj in list:
        attrs = obj["attributes"]["min"]
        attrs.insert(0,{
            "key": "Index",
            "value": index
        })
        index+=1
    return

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

def searchTreeThrough(start_object):
    tree = parseTree(None)
    found_object = None
    print start_object
    for child in tree["_parents"]:
        if start_object["Name"] == child["name"]:
            found_object = child
    if found_object == None:
        print "second level"
        for child in tree["_parents"]:
            object = getObjectById(child["id"])
            object["_parents"] = getNodeNeighbours(object,"2")
    else:
        filter_name = checkFilter(start_object)
        return {
            "filter_name": filter_name,
            "tree": tree,
            "path":[start_object["Name"]]
        }

def checkFilter(object):
    sample = getSample()
    rules = None
    if "filter_buttons" in sample:
        for filter in sample["filter_buttons"]:
            if "filter" in filter and "name" in filter:
                filterres = filterObjects([object],filter["filter"])
                if len(filterres)!=0:
                    return filter["name"]
    return rules

def parseTree(rules):
    global start_name
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

        result["_parents"]=getNodeNeighbours(result,"0",1,rules)
        return result

    if sample["root"]["type"]=="new":
        tree = parseObjectInfo(sample["root"],sample["root"]["fields"])
    return tree

def parseList():
    result = []
    samples = getSample()
    sample = samples["root"]

    basic_list = getObjects(parseRulesToString({},sample["filter"]))
    for base_obj in basic_list:
        obj = {"name":base_obj["Name"],"id":"","_parents":[]}
        obj["id"] = parseId(base_obj)
        display_details = sample["display_filter"]
        obj_attributes = parseAttributes(display_details,base_obj)
        obj["attributes"] = obj_attributes
        display_attributes = sample["display_attributes"]
        if "sort_field" in sample and "sort_type" in display_attributes and display_attributes["sort_type"]=="cells":
            #if sort_field is array than split on two objects
            sortname = sample["sort_field"]
            sortfield = next((x for x in obj_attributes["min"] if x["key"]==sortname),None)
            if sortfield and type(sortfield["value"]) is list:
                for sf_value in sortfield["value"]:
                    copyobj = copy.deepcopy(obj)
                    splitting_field = next((x for x in copyobj["attributes"]["min"] if x["key"]==sortname),None)
                    splitting_field["value"] = sf_value
                    result.append(copyobj)
            else:
                result.append(obj)
        else:
            result.append(obj)
    if "sort_field" in sample:
        sortfields = []
        if isinstance(sample["sort_field"],basestring):
            sortfields.append(sample["sort_field"])
        elif type(sample["sort_field"]) is list:
            sortfields = sample["sort_field"]
        for sortfield in sortfields:
            result = sorted(result, key=lambda k: next((attr for attr in k["attributes"]["min"] if attr["key"]==sortfield),{"value":""})["value"])
        if isinstance(sample["sort_field"],basestring):
            if "sort_type" in display_attributes and display_attributes["sort_type"]=="cells":
                result = listFillGaps(result,sample["sort_field"])
            if "sort_type" in display_attributes and display_attributes["sort_type"]=="numbered":
                listNumbering(result);
    return result

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
            next+=getNeighbours(object,step)
        return next
    #loop where we go through path and change current value (it might be an object if it's not the end of the path)
    for i in range(0,len(path)-1):
        next_vals = []
        for obj in values:
            next_vals += getObjectInChain(obj,path[i])
        values = next_vals
    if len(values)==0:
        return None
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
        template = getTemplate(value)
        if template:
            temp_field = next((x for x in template["fields"] if x["key"] == path[-1]), {})
        if "units" in temp_field:
            units = " " + str(temp_field["units"])
            value = unicode(value[path[-1]])+units
        else:
            value = value[path[-1]]
    return value

def getNeighbours(object,foreign_key):
    result = []
    if foreign_key in object:
        #create rules
        rules = {"Class":foreign_key,"Name":object[foreign_key],"System":object["System"]}
        #get object
        result.append(getObject(rules))
    else:
        rules = {"Class":foreign_key,"System":object["System"]}
        neighbours = getObjects(rules)
        link = {}
        for n in neighbours:
            link = getLink(object,n,{})
            if len(link)!=0:
                result.append(n)
    return result

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
            link = getLink(object,n,{})
            if len(link)!=0:
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
        pr_k = template["primary_key"]
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

def getTools(system_name):
    global tree_sample
    if system_name not in tree_sample:
        tree_sample[system_name] = getDataFile(system_name+"_sample.json")
    samples = tree_sample[system_name]
    return next((x for x in samples if x["name"] == "Tools"), None)

def getMenu(system_name):
    global tree_sample
    if system_name not in tree_sample:
        tree_sample[system_name] = getDataFile(system_name+"_sample.json")
    samples = tree_sample[system_name]
    return next((x for x in samples if x["name"] == "Menu"), None)

def getSample():
    global tree_sample,current_scheme_name
    system_name = current_scheme_name["system"]
    sample_link = current_scheme_name["sample"]
    #menu = getMenu(system_name)
    #sample_button = next((x for x in menu["buttons"] if x["link_name"] == sample_link), None)
    #if not sample_button:
    #    print "Error: no such menu button: "+ sample_link
    #    return None
    sample_name = sample_link#_button["sample"]
    samples = tree_sample[system_name]
    return next((x for x in samples if x["name"] == sample_name), None)

def getAllTemplates():
    global tree_template,current_scheme_name
    system_name = current_scheme_name["system"]
    if system_name not in tree_template:
        tree_template[system_name] = getDataFile(system_name+"_template.json")
    return tree_template[system_name]

def getAllObjects():
    global tree_data,current_scheme_name
    system_name = current_scheme_name["system"]
    if system_name not in tree_data:
        tree_data[system_name] = getDataFile(system_name+".json")
    return tree_data[system_name]

def getObjects(rules):
    data = getAllObjects()
    return filterObjects(data,rules)

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

def filterObjects(data,rules):
    objects = []
    def filter(o):
        result = True
        for r in rules:
            if rules[r]==None:
                result = False
            elif type(rules[r]) is unicode:
                if rules[r].startswith("has"):
                    if r in o and not re.search(rules[r][3:],o[r]):
                        result = False
                else:
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

def getFilter(filter_name):
    sample = getSample()
    rules = None
    if "filter_buttons" in sample:
        rules = next((x for x in sample["filter_buttons"] if x["name"] == filter_name), None)
    if rules and "filter" in rules:
        rules = rules["filter"]
    return rules

def getTemplate(object):
    if "Class" not in object:
        return None
    templates = getAllTemplates()
    for t in templates:
        if object["Class"]==t["class"]:
            return t

def getLinkDirectioned(obj1,obj2,temp1,temp2,link_pos,direction):
    links = []
    #check foreign keys
    if "foreign_keys" in temp1 and temp2["class"] in temp1["foreign_keys"] and temp2["class"] in obj1:
        linked = True
        for i in range(0,len(temp2["primary_key"])-1):
            check_field = temp2["primary_key"][i]
            if check_field=="Name":
                if obj1[temp2["class"]]!=obj2["Name"]:
                    linked = False
            elif check_field in obj1:
                if obj1[check_field]!=obj2[check_field]:
                    linked = False
            elif check_field in temp2["foreign_keys"] and check_field==temp1["class"]:
                if obj1["Name"]!=obj2[check_field]:
                    linked = False
            else:
                 linked = False
        if linked == True:
            #just don't know what to add
            links += [{
                "from": obj1["Name"],
                "to": obj2["Name"]
            }]
    #check components
    if "components" in temp1 and temp1["components"]:
        components = obj1[temp1["components"]]
        for l in components:
            linked = True
            for i in range(0,len(temp2["primary_key"])-1):
                field1 = temp1["component_check_values"][i]
                field2 = temp2["primary_key"][i]
                if field1=="Component_name":
                    if obj2["Class"] in l:
                        if l[obj2["Class"]]!=obj2[field2]:
                            linked = False
                    else:
                        linked = False
                elif field1 in l and l[field1]:
                    if l[field1]!=obj2[field2]:
                        linked = False
                else:
                    if obj1[field1]!=obj2[field2]:
                        linked = False
            if linked == True:
                if "component_ID" in temp1 and temp1["component_ID"]:
                    #l["link_id"] = l[temp1["component_ID"]]
                    link_pos[direction] = l[temp1["component_ID"]]
                links.append(l)
    return links

def getLink(obj1,obj2,link_pos):
    links = []
    link_pos["from"] = None
    link_pos["to"] = None
    temp1 = getTemplate(obj1)
    temp2 = getTemplate(obj2)
    links += getLinkDirectioned(obj1,obj2,temp1,temp2,link_pos,"from")
    links += getLinkDirectioned(obj2,obj1,temp2,temp1,link_pos,"to")
    return links

"""def getLink(obj1,obj2):
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
        for i in range(0,len(class2["primary_key"])-1):
            field2 = class2["primary_key"][i]
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
        for i in range(0,len(class2["primary_key"])-1):
            field1 = class1["component_check_values"][i]
            field2 = class2["primary_key"][i]
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
    return link"""


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