from enum import Enum
from .parser import Parser
from .definition import Path
import os
import shutil
from mako.lookup import TemplateLookup
from mako import template

template_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "template", "pybind11")
cache_path = os.path.join(template_path, "__template_cache__")

class GeneratorType(Enum):
    PYBIND11 = 1

class Generator():
    def __init__(self, root_path:str, module_name:str):
        self._root_path = root_path
        self._module_name = module_name

    def start(self, parser:Parser):
        pass

class Generator_Pybind11(Generator):
    def __init__(self, root_path, module_name):
        super().__init__(root_path, module_name)

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
        for metadata in parser.metadatas:
            path:Path = metadata['path']
            create_directories.add(path.local_root)
            data = metadata['data']
            code = dict()
            code['include_files'] = [path.filename]
            code['export_file_name'] = 'Bind_{}'.format(path.filename.split('.')[0])
            code['file_path'] = os.path.join(abs_path, 
                                             path.local_root, 
                                             '{}.h'.format(code['export_file_name']))
            main_include_files.append('{}/{}'.format(path.local_root, 
                                                     '{}.h'.format(code['export_file_name'])))
            clz_infos = []
            code['clz_infos'] = clz_infos
            for clz_name, clz_info in data.items():
                new_info = dict()
                clz_infos.append(new_info)
                new_info['name'] = clz_name
                meta_info = clz_info.get('meta_info')
                new_info['comment'] = meta_info.get('comment', '')
                new_info['is_singleton'] = meta_info.get('is_singleton', 0)
                funcs = clz_info.get('funcs')
                funcs_data = []
                for func in funcs:
                    meta_info = func.get('meta_info')
                    funcs_data.append(dict(name = func['name'], 
                                           comment = meta_info.get("comment", "")))
                new_info['funcs'] = funcs_data
            codes.append(code)
            # t = lookup.get_template("Bind.Template")
        
        for dir in create_directories:
            dir = os.path.join(abs_path, dir)
            if not os.path.exists(dir):
                os.mkdir(dir)

        imported_funcs = []
        for code in codes:
            imported_funcs.append(code['export_file_name'])
            with open( code['file_path'], 'w') as f:
                t = lookup.get_template("Bind.Template")
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

def GeneratorFactory(root_path, module_name, e: GeneratorType = GeneratorType.PYBIND11):        
    if e == GeneratorType.PYBIND11:
        return Generator_Pybind11(root_path, module_name)