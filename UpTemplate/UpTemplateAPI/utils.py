from django.contrib.contenttypes.models import ContentType
import re


def set_cct(cct_list: list[ContentType], app_label, model_list):
    for index in range(len(cct_list)):
        cct_list[index].app_label = app_label
        cct_list[index].model = model_list[index]
        cct_list[index].save()


from collections import OrderedDict

def ordered_dict_to_dict(ordered_dict):
    if isinstance(ordered_dict, dict):
        return {
            key: ordered_dict_to_dict(value) if isinstance(value, OrderedDict) else value
            for key, value in ordered_dict.items()
        }
    return ordered_dict





def flatten_dict(dict_obj, field_name):

    temp_dict = dict_obj.pop(field_name)
    for (key, value) in temp_dict.items():
        if key not in ['id']:
            dict_obj[key] = value
    
    return dict_obj

MODELS_TYPE_TO_FIELDS = {
    "rect": ["width", "height"]
}


def camel_to_snake(dictionary):
    snake_dict = {}
    for key, value in dictionary.items():
        snake_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
        snake_dict[snake_key] = value
    return snake_dict


def flattern_to_nested(dictionary, fields, field_name):
    res = {field_name:{}}
    for key, value in dictionary.items():
        if key in fields:
            res[field_name][key] = value
        else:
            res[key] = value

    return res

def clone_value_after_index(value, my_list):
    if value in my_list:
        index = my_list.index(value)
        new_list = my_list[:index + 1] + [value] + my_list[index + 1:]
        return new_list
    else:
        return my_list + [value]