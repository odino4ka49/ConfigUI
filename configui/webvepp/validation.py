# -*- coding: utf-8 -*-
__author__ = 'oidin'
import json
import inspect, os
import codecs

system_name = "CHAN"
objects = []
templates = []
template_required_fields = ["class","comment","fields","primary_key"]
logfile = None

def setSystemName(sname):
    global system_name
    system_name = sname

def getSystemName():
    global system_name
    return system_name

def getAllTemplates():
    global system_name
    tree_template = getDataFile(system_name+"_template.json")
    return tree_template

def getTemplate(object):
    if "Class" not in object:
        log(object,None,"No 'Class' field in the object.")
        return None
    for t in templates:
        if object["Class"]==t["class"]:
            return t
    return None

def getTemplateByName(classname):
    for t in templates:
        if classname==t["class"]:
            return t
    return None

def getAllObjects():
    global system_name
    return getDataFile(system_name+".json")

def filterObjects(data,rules):
    objects = []
    def filter(o):
        result = True
        for r in rules:
            if rules[r]==None:
                result = False
            elif type(rules[r]) is unicode:
                if rules[r].startswith("has"):
                    if r in o and not r.search(rules[r][3:],o[r]):
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

def getObjects(rules):
    data = objects
    return filterObjects(data,rules)

def validateObject(object,template):
    result = True
    if not template:
        log(object,template,"There is no such class.")
        return False
    #is there some fields in object that template doesn't have?
    for field in object:
        if field != "Class":
            temp_f = next((x for x in template["fields"] if x["key"] == field), None)
            if temp_f==None:
                log(object,template,"There is no such field in class: "+field +".")
                result = False
    for field in template["fields"]:
        #is there such field in object?
        if field["key"] not in object:
            log_warning(object,template,"There is no such field in object: "+field["key"] +".")
            result = False
        #what about type?
        else:
            is_right_type = True
            if field["type"]=="string":
                if not isinstance(object[field["key"]], basestring):
                   is_right_type = False
            elif field["type"]=="integer":
                if not isinstance(object[field["key"]], int):
                    is_right_type = False
            elif field["type"]=="array":
                if not isinstance(object[field["key"]], list):
                    is_right_type = False
            elif field["type"]=="float":
                if not isinstance(object[field["key"]], (float,int)):
                    is_right_type = False
            elif field["type"]=="double":
                if not isinstance(object[field["key"]], (float,int,long)):
                    is_right_type = False
            elif field["type"]=="boolean":
                if not isinstance(object[field["key"]], bool):
                    is_right_type = False
            if object[field["key"]]==None:
                is_right_type = True
            if field["type"] in ["integer","double","float"] and "limits" in field and field["limits"]:
                if object[field["key"]]<field["limits"][0] or object[field["key"]]>field["limits"][1]:
                    log(object,template,"Out of limits: "+ field["key"])
                    result = False
            if "values" in field and field["values"]:
                print field
                if object[field["key"]] not in field["values"]:
                    log(object,template,"Not in possible values: "+ field["key"])
            if not is_right_type:
                log(object,template,"Wrong type of the field: "+ field["key"] +". It actually is "+type(object[field["key"]]).__name__)
                result = False
    #what about primary_key?
    if "primary_key" in template:
        rules = {"Class":object["Class"]}
        for field_name in template["primary_key"]:
            if field_name not in object:
                log(object,template,"Primary key is wrong. There is no such field in object: "+field_name +".")
                result = False
                break
            else:
                rules[field_name] = object[field_name]
        similar = getObjects(rules)
        if len(similar)>1:
            log(object,template,"There is another object with the same primary key.")
            result = False
    else:
        log(object,template,"There is no primary key in class.")
        result = False
    #check foreign keys
    if "foreign_keys" in template:
        for fk in template["foreign_keys"]:
            if fk in object:
                if object[fk]:
                    rules = {"Class":fk,"Name":object[fk],"System":object["System"]}
                    neighbours = len(getObjects(rules))
                    if neighbours<1:
                        log(object,template,"There is no such object: {"+fk+": "+object[fk]+"}")
                        result = False
                    elif neighbours>1:
                        log(object,template,"There are several objects on this foreign key: {"+fk+": "+object[fk]+"}")
                        result = False
            else:
                log_warning(object,template,"Object doesn't have this foreign key: "+fk+".")
                result = False
    #component check
    if "components" in template and template["components"]:
        if "component_ID" not in template or "component_types" not in template or not template["component_types"] or "component_check_values" not in template or not template["component_check_values"]:
            log(object,template,"There are problems with template. Validate your template file. Should have all component attributes.")
            result = False
        else:
            comp_name = template["components"]
            if comp_name not in object:
                log(object,template,"There is no such field: "+comp_name+".")
                result = False
            else:
                #check fields and their class and uniqueness of id and existence
                ids = []
                components = object[comp_name]
                for component in components:
                    if template["component_ID"] not in component and template["component_ID"]:
                        log(object,template,"There is no such field: "+template["component_ID"]+" in the component.")
                        result = False
                    for comp_field in component:
                        if comp_field != template["component_ID"]:
                            #then comp_field is the class of object for us
                            if comp_field in template["component_types"]:
                                #get checklist for components
                                checklist = template["component_check_values"]
                                #get template of the other class
                                comp_templ = getTemplateByName(comp_field)
                                #check if there are such fields in the object and create rules
                                if len(checklist)!=len(comp_templ["primary_key"]):
                                    log(object,template,"There are problems with template. Validate your template file. Component_check_values and primary_key.")
                                    result = False
                                else:
                                    rules = {"Class":comp_field}
                                    for i in range(0,len(comp_templ["primary_key"])):
                                        cfield = checklist[i]
                                        pfield = comp_templ["primary_key"][i]
                                        if cfield=="Component_name":
                                            if pfield=="Name":
                                                rules["Name"] = component[comp_field]
                                            else:
                                                log(object,template,"There are problems with template. Validate your template file. Component name and Name.")
                                                result = False
                                        elif cfield not in object:
                                            log(object,template,"There is no such field: "+cfield+" in object. You should validate your template file. Component_check_value is not found in object.")
                                            result = False
                                        else:
                                            rules[pfield] = object[cfield]
                                    #find such an object
                                    neighbours = len(getObjects(rules))
                                    if neighbours<1:
                                        log(object,template,"There is no such object: "+unicode(rules)+"}")
                                        result = False
                                    elif neighbours>1:
                                        log(object,template,"There are several objects on this foreign key: "+unicode(rules)+"}")
                                        result = False
                        else:
                            id = component[comp_field]
                            if id in ids:
                                log(object,template,"There are not unique id for components: "+str(id)+".")
                                result = False
                            else:
                                ids.append(component[comp_field])
    #additional check
    return result

def checkUniqueness(template,field):
    result = True
    values = []
    for object in objects:
        if "Class" in object and "class" in template and object["Class"]==template["class"]:
            if field in object:
                if object[field] in values:
                    log(object,template,"Field value is not unique: "+field+".")
                    result = False
                else:
                    values.append(object[field])
    return result

def validateTemplate(template):
    result = True
    fields_names = []
    for rfield in template_required_fields:
        if rfield not in template:
            log_temp(template,"There is no such field: "+rfield+".")
    if "fields" in template:
        for field in template["fields"]:
            if "key" in field:
                if field["key"] in fields_names:
                    log_temp(template,"Field name is not unique: "+field["key"]+".")
                    result = False
                else:
                    fields_names.append(field["key"])
    for rfield in template:
        if rfield=="class" or rfield=="comment":
            if not isinstance(template[rfield], basestring):
                log_temp(template,"Wrong type of data in field: "+rfield+". Should be String.")
                result = False
        elif rfield=="fields":
            for ofield in template["fields"]:
                if "key" in ofield:
                    if not isinstance(ofield["key"], basestring):
                        log_temp(template,"Wrong type of data in field: fields/key for key "+ofield["key"]+". Should be string")
                        result = False
                else:
                    log_temp(template,"There is no field: fields/key.")
                    result = False
                if "type" in ofield:
                    if not isinstance(ofield["type"], basestring):
                        log_temp(template,"Wrong type of data in field: fields/type. Should be string")
                        result = False
                else:
                    log_temp(template,"There is no field: fields/type.")
                    result = False
                if "uniqueness" in ofield and ofield["uniqueness"]:
                    if "key" in ofield and not checkUniqueness(template,ofield["key"]):
                        result = False
                if "limits" in ofield and ofield["limits"]:
                    if not isinstance(ofield["limits"], list):
                        log_temp(template,"Wrong type of data in field: fields/limits. Should be array")
                        result = False
                    if len(ofield["limits"])!=2:
                        log_temp(template,"Wrong number of elements in: fields/limits. Should be 2")
                        result = False
                    if ofield["type"] not in ["integer","float","double"]:
                        log_temp(template,"Wrong type of elements in: fields/type. It has limits")
                        result = False
                if "values" in ofield and ofield["values"]:
                    if not isinstance(ofield["values"], list):
                        log_temp(template,"Wrong type of data in field: fields/values. Should be array")
                        result = False
                if "units" in ofield and ofield["units"]:
                    if not isinstance(ofield["units"], basestring):
                        log_temp(template,"Wrong type of data in field: fields/units. Should be string")
                        result = False
                for key in ofield:
                    if key!="key" and key!="type" and key!="uniqueness" and key!="units" and key!="limits" and key!="values":
                        log_temp(template,"There is a weird field in fields of template: "+key+".")
                        result = False
        elif rfield=="foreign_keys":
            if not isinstance(template[rfield], list):
                log_temp(template,"Wrong type of data in field: "+rfield+". Should be Array.")
                result = False
            else:
                for key in template[rfield]:
                    if not isinstance(key, basestring):
                        log_temp(template,"Wrong type of data in field foreign_keys for key "+key+". Should be string")
                        result = False
                    else:
                        #check if template has such field
                        if key not in fields_names:
                            log_temp(template,"There is a problem with foreign_keys. There are no such field "+key+".")
                            result = False
                        #check if there's such class
                        found = False
                        for templ in templates:
                            if "class" in templ and templ["class"]==key:
                                found=True
                        if not found:
                            log_temp(template,"There are no template for "+key+" from component_types.")
                            result = False
        elif rfield=="primary_key":
            if not isinstance(template[rfield], list):
                log_temp(template,"Wrong type of data in field: "+rfield+". Should be Array.")
                result = False
            else:
                for key in template[rfield]:
                    if not isinstance(key, basestring):
                        log_temp(template,"Wrong type of data in field primary_key for key "+key+". Should be string")
                        result = False
                    else:
                        #check if template has such field
                        if key not in fields_names:
                            log_msg(unicode(fields_names)+":"+key)
                            log_temp(template,"There is a problem with primary_key. There are no such field "+key+".")
                            result = False
        elif rfield=="components":
            if template["components"]:
                if not isinstance(template["components"], basestring):
                    log_temp(template,"Wrong type of data in field components. Should be string")
                    result = False
                else:
                    if template["components"] not in fields_names:
                        log_temp(template,"There is a problem with components. There are no such field "+template["components"]+".")
                        result = False
                    else:
                        if "component_ID" not in template:
                            log_temp(template,"There are supposed to be component_ID field.")
                            result = False
                        if "component_types" not in template:
                            log_temp(template,"There are supposed to be component_types field.")
                            result = False
                        else:
                            if not template["component_types"]:
                                log_temp(template,"component_types field is not supposed to be null.")
                                result = False
                        if "component_check_values" not in template:
                            log_temp(template,"There are supposed to be component_check_values field.")
                            result = False
                        else:
                            if not template["component_check_values"]:
                                log_temp(template,"component_check_values field is not supposed to be null.")
                                result = False
        elif rfield=="component_ID":
            if template["component_ID"]:
                if not isinstance(template["component_ID"], basestring):
                    log_temp(template,"Wrong type of data in field component_ID. Should be string")
                    result = False
            if "components" not in template:
                log_temp(template,"There are supposed to be components field.")
                result = False
        elif rfield=="component_types":
            if template["component_types"]:
                if not isinstance(template["component_types"], list):
                    log_temp(template,"Wrong type of data in field: "+rfield+". Should be Array.")
                    result = False
                else:
                    for ctype in template["component_types"]:
                        if not isinstance(ctype, basestring):
                            log_temp(template,"Wrong type of data in field: "+ctype+". Should be string.")
                            result = False
                        else:
                            found = False
                            for templ in templates:
                                if "class" in templ and templ["class"]==ctype:
                                    found=True
                                    #let's check primary_key and component_check_values
                                    if "primary_key" in templ and "component_check_values" in template:
                                        check_list = template["component_check_values"]
                                        pk_list = templ["primary_key"]
                                        if len(check_list)==len(pk_list):
                                            for i in range(0,len(check_list)-1):
                                                if check_list[i]=="Component_name":
                                                    if pk_list[i]!="Name":
                                                        log_temp(template,"There are supposed to be conformity of fields Name and Component_name for class: "+ctype+".")
                                                        result = False
                                                if "fields" in template:
                                                    if(check_list[i]=="Component_name"):
                                                        check_field = next((x for x in template["fields"] if x["key"] == "Name"), None)
                                                    else:
                                                        check_field = next((x for x in template["fields"] if x["key"] == check_list[i]), None)
                                                if "fields" in templ:
                                                    pk_field = next((x for x in template["fields"] if x["key"] == pk_list[i]), None)
                                                if "type" in check_field and "type" in pk_field and check_field["type"]!=pk_field["type"]:
                                                    log_temp(template,"Different types of field "+pk_list[i]+" in class: "+ctype+".")
                                                    result = False
                                        else:
                                            log_temp(template,"There are different lengths for primary_key and component_check_values for class: "+ctype+".")
                                            result = False
                            if not found:
                                log_temp(template,"There are no template for "+ctype+" from component_types.")
                                result = False
            if "components" not in template:
                log_temp(template,"There are supposed to be components field.")
                result = False
        elif rfield=="component_check_values":
            if template["component_check_values"]:
                if not isinstance(template["component_types"], list):
                    log_temp(template,"Wrong type of data in field: "+rfield+". Should be Array.")
                    result = False
                else:
                    for key in template["component_check_values"]:
                        if not isinstance(ctype, basestring):
                            log_temp(template,"Wrong type of data in field: "+key+". Should be string.")
                            result = False
                        else:
                            if key!="Component_name":
                                if key not in fields_names:
                                    log_temp(template,"There is a problem with component_check_values. There are no such field "+key+".")
                                    result = False
            if "components" not in template:
                log_temp(template,"There are supposed to be components field.")
                result = False
        else:
            log_temp(template,"There are not supposed to be field "+rfield+" in this template.")
            result = False
    return result

def log_msg(message):
    logfile.write(message+"\n")

def log_temp(template,message):
    if "class" not in template:
        template_name = unicode(template)
    else:
        template_name = unicode(template["class"])
    print template_name
    logfile.write("Error: tempate "+template_name+". "+message+"\n")
    return 0

def log_warning(object,template,message):
    object_name = ""
    if "Class" not in object:
        object_name = unicode(object)
    elif not template or "primary_key" not in template:
        object_name = object["Class"]+"/"
        if "System" in object:
            object_name += object["System"]+"/"
        if "Name" in object:
            object_name += object["Name"]
    else:
        object_name = object["Class"]+"/"
        for pk in template["primary_key"]:
            object_name+=object[pk]+"/"
    logfile.write("Warning: object '"+object_name+"'. "+message+"\n")
    return 0

def log(object,template,message):
    object_name = ""
    if "Class" not in object:
        object_name = unicode(object)
    elif not template or "primary_key" not in template:
        object_name = object["Class"]+"/"
        if "System" in object:
            object_name += object["System"]+"/"
        if "Name" in object:
            object_name += object["Name"]
    else:
        object_name = object["Class"]+"/"
        for pk in template["primary_key"]:
            object_name+=object[pk]+"/"
    logfile.write("Error: object '"+object_name+"'. "+message+"\n")
    return 0

def getDataFile(name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name) as data_file:
        data = json.load(data_file)
    return data

def validate():
    global objects,templates
    objects = getAllObjects()
    #load templates
    templates = getAllTemplates()
    for template in templates:
        validateTemplate(template)
    for object in objects:
        #call function of checking with object and template
        validateObject(object,getTemplate(object))

def getValidationLog():
    global file_name,logfile,system_name
    file_name = os.path.dirname(os.path.abspath(__file__))+"/descriptions/validation_log/validation_log.txt"
    logfile = codecs.open(file_name,"w","utf-8")
    logfile.write("System name: " + system_name+"\n")
    validate()
    logfile.close()
    with open(file_name, 'r') as myfile:
        data=myfile.read()#.replace('\n', '')
    return data

#load objects
"""file_name = os.path.dirname(os.path.abspath(__file__))+"/descriptions/validation_log/validation_log.txt"
logfile = open(file_name,"w")
objects = getAllObjects()
#load templates
templates = getAllTemplates()
#create log object
file_output_name = file_name.replace('json','txt')
for template in templates:
    validateTemplate(template)
for object in objects:
    #call function of checking with object and template
    validateObject(object,getTemplate(object))
logfile.close()"""
