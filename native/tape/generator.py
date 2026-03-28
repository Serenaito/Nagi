from enum import Enum
from .parser import Parser
from .definition import Path
import os
import shutil
from mako.lookup import TemplateLookup
from mako import template

template_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "template", "pybind11")
cache_path = os.path.join(template_path, "__template_cache__")
cmake_path = '{}\n${{CMAKE_CURRENT_SOURCE_DIR}}/{}'
cmake_file_name = "generate.cmake"
class GeneratorType(Enum):
    PYBIND11 = 1

class Generator():
    def __init__(self, root_path:str, module_name:str):
        self._root_path = root_path
        self._module_name = module_name

    def start(self, parser:Parser) -> list[str]:
        pass

class Generator_Pybind11(Generator):
    def __init__(self, root_path, module_name):
        super().__init__(root_path, module_name)

    @staticmethod
    def __handle_singleton_class(out_data:dict, clz_name, clz_info:dict, meta_info:dict):
        if"singleton_method" not in meta_info:
            return False
        out_data['override_constructor'] = 0
        out_data['is_wrapper'] = 1
        out_data['singleton_method'] = meta_info['singleton_method']
        funcs_data = []
        funcs = clz_info.get('funcs')
        access_symbol = '.'
        if meta_info['singleton_pointer']:
            access_symbol = '->'
        for func in funcs:
            is_static = func['is_static']
            if is_static != 1 :
                params_str = ""
                params_def_str = ""
                arg_type_list = func['arg_type_list']

                for i in range(0, len(arg_type_list)):
                    if i == 0:
                        params_str = "arg{}".format(i)
                        params_def_str = "{} arg{}".format(arg_type_list[i], i)
                    else:
                        params_str = "{}, arg{}".format(params_str, i)
                        params_def_str = "{}, {} arg{}".format(params_def_str, arg_type_list[i], i)
                name = func['name']
                funcs_data.append(dict(name = name, real_name="Call_{}_{}".format(clz_name, name),
                                   is_static = is_static,
                                   return_type = func['return_type'],
                                   arg_list_str = params_str,
                                   arg_list_def_str = params_def_str,
                                   access_symbol = access_symbol,
                                   comment = func.get("comment", "")))
            else:
                funcs_data.append(dict(name = func['name'], is_static = is_static,
                                   comment = func.get("comment", "")))
        out_data['funcs'] = funcs_data
        return True

    @staticmethod        
    def __handle_class(out_data:dict, clz_info:dict):
        out_data['is_wrapper'] = 0
        constructors = clz_info.get('constructors')
        if len(constructors) > 0:
            constructors_str = []
            for constructor in constructors:
                index = 1
                arg_type_str = ''
                for arg_type in constructor:
                    if index == 1:
                        arg_type_str = arg_type
                    else:
                        arg_type_str = '{}, {}'.format(arg_type_str, arg_type)
                    index = index + 1
                constructors_str.append(arg_type_str)
            out_data['constructors'] = constructors_str
            out_data['override_constructor'] = 1
        else:
            out_data['override_constructor'] = 0
        funcs = clz_info.get('funcs')
        funcs_data = []
        for func in funcs:
            funcs_data.append(dict(name = func['name'], 
                                   is_static = func['is_static'],
                                   comment = func.get("comment", "")))
        out_data['funcs'] = funcs_data
    def start(self, parser):
        abs_path = os.path.abspath(self._root_path)
        if os.path.exists(abs_path):
            shutil.rmtree(abs_path)
        os.mkdir(abs_path)
        parser.ananlysis()
        lookup = TemplateLookup(directories=[template_path], module_directory = cache_path)
        main_include_files = []
        create_directories = set()
        codes = []
        cmake_files = ''
        export_symbol = []
        print(parser.metadatas)
        for metadata in parser.metadatas:
            path:Path = metadata['path']
            create_directories.add(path.local_root)
            data = metadata['data']
            code = dict()
            code['include_files'] = [path.filename]
            code['export_file_name'] = 'Bind_{}'.format(path.filename.split('.')[0])
            file_name = '{}.h'.format(code['export_file_name'])
            code['file_path'] = os.path.join(abs_path, 
                                             path.local_root, 
                                             file_name)
            cmake_files = cmake_path.format(cmake_files, '{}/{}/{}'.format(self._root_path,
                                                                           path.local_root, 
                                                                           file_name))
            main_include_files.append('{}/{}'.format(path.local_root, 
                                                     '{}.h'.format(code['export_file_name'])))
            clz_infos = []
            code['clz_infos'] = clz_infos
            for clz_name, clz_info in data.items():
                new_info = dict()
                clz_infos.append(new_info)
                export_symbol.append(clz_name)
                new_info['name'] = clz_name
                meta_info = clz_info.get('meta_info')
                new_info['comment'] = meta_info.get('comment', '')
                new_info['is_singleton'] = meta_info.get('is_singleton', 0)
                if not Generator_Pybind11.__handle_singleton_class(new_info, clz_name, clz_info, meta_info):
                    Generator_Pybind11.__handle_class(new_info, clz_info)
            codes.append(code)
        
        for dir in create_directories:
            dir = os.path.join(abs_path, dir)
            if not os.path.exists(dir):
                os.mkdir(dir)

        imported_funcs = []
        for code in codes:
            imported_funcs.append(code['export_file_name'])
            with open( code['file_path'], 'w') as f:
                t = lookup.get_template("Bind.Template")
                # print(code)
                code = t.render(code = code)
                f.write(code.replace('\r',''))
        file_path = os.path.join(abs_path, 'Bind_Main.cpp')
        with open(file_path, 'w') as f:
            t = lookup.get_template("BindCpp.Template")
            code = t.render(include_files = main_include_files,
                            bind_module_name = self._module_name,
                            doc_comment = "test",
                            imported_funcs = imported_funcs)
            f.write(code.replace('\r',''))
        cmake_files = cmake_path.format(cmake_files, '{}/Bind_Main.cpp'.format(self._root_path))
        with open(os.path.join(abs_path, cmake_file_name), 'w') as f:
            f.write('''
set(GENERATE_FILES
{}
)                    '''.format(cmake_files))
        return export_symbol


def GeneratorFactory(root_path, module_name, e: GeneratorType = GeneratorType.PYBIND11):        
    if e == GeneratorType.PYBIND11:
        return Generator_Pybind11(root_path, module_name)