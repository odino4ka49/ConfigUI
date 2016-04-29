__author__ = 'oidin'
import json
import inspect, os

system_name = "CHAN"
objects = []
templates = []

def getAllTemplates():
    if system_name == "CHAN":
        tree_template = getDataFile("Chan_template.json")
    elif system_name == "V4":
        tree_template = getDataFile("Chan_template.json")
    else:
        tree_template = []
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
    if system_name == "CHAN":
        return getDataFile("CHAN.json")
    elif system_name == "V4":
        return getDataFile("V4.json")
    else:
        return []

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
            log(object,template,"There is no such field in object: "+field["key"] +".")
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
                log(object,template,"Object doesn't have this foreign key: "+fk+".")
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
    print("Error: In the object "+object_name+" there is a problem. "+message)
    return 0

def getDataFile(name):
    with open(os.path.dirname(os.path.abspath(__file__))+'/descriptions/'+name) as data_file:
        data = json.load(data_file)
    return data

#load objects
file_name = system_name+".json"
objects = getAllObjects()
#load templates
templates = getAllTemplates()
#create log object
file_output_name = file_name.replace('json','txt')
for object in objects:
    #call function of checking with object and template
    validateObject(object,getTemplate(object))
