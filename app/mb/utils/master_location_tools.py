from mb.models import MasterHabitat
from django.db import models
from mb.models.location_models import MasterLocation

def get_master_habitats(ml : MasterLocation):
    """ Get MasterHabitats by MasterLocation """ 
    mr = ml.reference

    try:
        master_habitats = MasterHabitat.objects.filter(reference=mr)
    except:
        return "nan"
    
    habitats = ""

    for master_habitat in master_habitats:
        habitats = habitats + f"{master_habitat.name} "

    return str(habitats)

def string_contains(str1, str2):
    """ If string contains substring. Converts string to lowercase. """
    if str1.lower() in str2.lower():
        return True
    return False

def remove_none_values(list):
    """ Delete None-values from list. """
    new_list = []
    for item in list:
        if item == None:
            continue
        new_list.append(item)
    return new_list

def filter(objects, params):
    """ This operates filter from web site. """    
    try:
        master_location = str(params["master_location"])
        for i in range(len(objects)):
            if master_location == "":
                break
            if string_contains(master_location, objects[i].name) == False:
                objects[i] = None
    except Exception as e:
        pass
    
    objects = remove_none_values(objects)
    try:
        reference = str(params["reference"])
        for i in range(len(objects)):
            if reference == "":
                break
            if string_contains(reference, objects[i].reference) == False:
                objects[i] = None
    except Exception as e:
        pass
            
    objects = remove_none_values(objects)
    try:
        master_habitat = params["master_habitat"]
        for i in range(len(objects)):
            if master_habitat == "":
                break
            if string_contains(master_habitat, objects[i].master_habitat) == False:
                objects[i] = None
    except Exception as e:
        pass
    
    objects = remove_none_values(objects)
    return objects