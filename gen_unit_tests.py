# -*- coding: utf-8 -*-

import sys
import os
from os import listdir
from os.path import isfile, join
import re


def parse_functions(file_path, get_docstrings=False):
    path_items = file_path.split(os.path.sep)
    module = u'.'.join(path_items[1:-1])
    # remove file extension
    module = module + u'.' + path_items[-1].split('.')[0]
    from_str = u"from " + module + u" import "
    from_l = []
    inputs_types = []
    dict_fun_inputs = dict()
    with open(file_path, 'r') as f:
        f_content = f.read()
    matches = re.findall( r'def.*:', f_content)
    for match in matches:
        match = ''.join(match.split()[1:])
        broken_match = re.split("\(|\)", match)
        fun_name, inputs = broken_match[0], broken_match[1:-1]
        from_l.append(fun_name)
        inputs = inputs[0].split(',')
        # remove default value attribution
        inputs = [v.split('=')[0] for v in inputs]
        dict_fun_inputs[fun_name] = inputs
        
    if get_docstrings:
        ds_matches = re.findall(r'(?:\n[\t ]*)\"{3}(.*?)\"{3}', f_content, re.M | re.S)            
        if len(ds_matches) == len(matches):
            for ds_match in ds_matches:
                result = re.search(r'Args:(.*)Returns:', ds_match, flags=re.S)
                if result is None:
                    result = re.search(r'Args:(.*)', ds_match, flags=re.S)
                inputs_types = inputs_types + re.findall(r'\(.*\)', result.group(1).strip())
        return dict_fun_inputs, from_str + ','.join(from_l) + "\n\n", [parse_string_tuple(s) for s in inputs_types]
    return dict_fun_inputs, from_str + ','.join(from_l) + "\n\n", None


def parse_string_tuple(s):
    return s[1:-1].split(', ')


def translate_parsed_function(fun_name, inputs, sep = "_"):    
    inputs_str = ','.join(inputs)
    class_name = u"Test" + ''.join([v.capitalize() for v in fun_name.split(sep)])
    test_fun_name = u"test_" + fun_name
    inst_attes = ("\n" + ' ' * 8).join([input + u" = {}" for input in inputs])
    return [class_name, test_fun_name, inst_attes, fun_name, inputs_str]


def translate_parsed_functions(d):
    list_class_decl = []
    class_decl_s = """class {}(object):
    def {}(self):
        # inputs instantiation
        {}
        # call the function on the instantiated attributes
        {}({})
        assert True"""

    for fun_name, inputs in d.items():
        list_class_decl.append(class_decl_s.format(*translate_parsed_function(fun_name, inputs)))
    return "\n\n".join(list_class_decl)


def set_init_configs(inputs_types, translate_parsed_functions_, stop_imports):
    l = []
    import_list = []
    import_str = None
    if inputs_types is not None:
        for inputs_type in inputs_types:
            if len(inputs_type) == 2:
                a, b = inputs_type
                if b == "optional":
                    l.append("None")
            else:
                a = inputs_type[0]
                l.append(a + u"()")
                import_list.append(a.split('.')[0])
        import_list = list(set(import_list))
        import_list = [v for v in import_list if v not in stop_imports]
        if import_list:
            import_str = u"import " + ",".join(import_list) + "\n\n"
        translate_parsed_functions_ = translate_parsed_functions_.format(*l)
    else:
        translate_parsed_functions_ = translate_parsed_functions_.replace("{}", "None")
    return import_str, translate_parsed_functions_


def write_to_test_file_path(file_path, test_file_path, get_docstrings, stop_imports):
    with open(test_file_path, 'w') as f:
        d, from_str, inputs_types = parse_functions(file_path, get_docstrings)
        f.write(from_str)
        translate_parsed_functions_ = translate_parsed_functions(d)
        import_str, translate_parsed_functions_ = set_init_configs(inputs_types, translate_parsed_functions_, stop_imports)
        if import_str is not None:
            f.write(import_str)
        f.write(translate_parsed_functions_)


def main(stop_imports):
    # by default, could be src
    proj_folder = sys.argv[1]
    origin_folder = sys.argv[2]
    test_folder = sys.argv[3]
    get_docstrings = sys.argv[4] == "True"
    print(get_docstrings)
    single_file_path = None
    if len(sys.argv) > 5:
        single_file_path = sys.argv[5]
    walk_dir = os.path.join(proj_folder, origin_folder)
    init_file_name = "__init__.py"
    stop_words = ["__init__.py"]
    stop_dir = ["__pycache__"]
    for root, subdirs, files in os.walk(walk_dir):
        path_items = root.split(os.path.sep)
        if path_items[-1] not in stop_dir:
            print('--\nroot = ' + root)
            
            test_dir_path = os.path.join(path_items[0], test_folder, *path_items[2:])
            init_file_path = os.path.join(test_dir_path, init_file_name)
            try:
                os.mkdir(test_dir_path)
            except OSError:
                print ("Creation of the directory %s failed" % test_dir_path)
            else:
                print ("Successfully created the directory %s" % test_dir_path)
            # create empty __init__.py file
            open(init_file_path, 'w').close()
    
            py_files = [f for f in files if f.split('.')[-1] == 'py' and f not in stop_words and f == "_utils.py"]
            for py_file in py_files:                        
                file_path = os.path.join(root, py_file)
                test_file_path = os.path.join(test_dir_path, u"test_" + py_file)
                if single_file_path is not None:
                    if file_path == single_file_path:
                        write_to_test_file_path(file_path, test_file_path, get_docstrings, stop_imports)
                        return
                else:                        
                    write_to_test_file_path(file_path, test_file_path, get_docstrings, stop_imports)


if __name__ == "__main__":
    stop_imports = ["float", "str", "dict", "tuple", "list", "int"]
    main(stop_imports)
