import pybind11
import argparse
import os
import shutil
import sys
import subprocess
import tape.parser, tape.generator
import time

if __name__ == '__main__':
    src_path = os.path.abspath('.')
    parent_path = os.path.abspath('../')
    python_bind_path = os.path.join(parent_path, "nagi_native") 
    python_bind_lib_path = os.path.join(python_bind_path, "lib").replace('\\',"/")
    module_cpp_name = "nagi_cpp_ex"
    module_py_name = "nagi_cpp"
    print(parent_path)
    print(src_path)
    print(python_bind_path)    
    print(python_bind_lib_path)
    parser = argparse.ArgumentParser()
    parser.add_argument('--rebuild', type=int, help='if set 1 clean project and build')
    parser.add_argument('--test', help='if set 1 clean project and build')
    parser.add_argument('--tape', help='just tape')
    args = parser.parse_args()
    parser = tape.parser.Parser()
    generator = tape.generator.GeneratorFactory("generate", "nagi_cpp_ex")
    parser.add_include_directories('./include')
    parser.add_include_directories('./tape/include')
    parser.add_include_directories(pybind11.get_include())
    parser.add_bind_directory("include")
    export_symbol = generator.start(parser)
    exit()
    export_symbol_str = ''
    for symbol in export_symbol:
        export_symbol_str = '{}\n{} = {}.{}'.format(export_symbol_str, symbol, module_cpp_name, symbol)

    build_path = os.path.join(src_path, "build")
    if os.path.exists(build_path):
        if args.rebuild == 1:
            shutil.rmtree(build_path)
            print('rm {} success'.format(build_path))
            os.mkdir(build_path)
    else:
        os.mkdir(build_path)

    if not os.path.exists(python_bind_path):
        os.mkdir(python_bind_path)

    if not os.path.exists(python_bind_lib_path):
        os.mkdir(python_bind_lib_path)
    cmd = 'cmake -B build'
    cmd = cmd + ' -D pybind11_DIR:PATH={}'.format(pybind11.get_cmake_dir())
    cmd = cmd + ' -DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={}'.format(python_bind_lib_path)
    cmd = cmd + ' && cmake --build build --config Release -j4'
    print("-------------------")
    print(cmd)
    print("-------------------")
    subprocess.run(cmd, shell=True)
    with open(os.path.join(python_bind_path, "__init__.py"), 'wb+') as init_file:
        init_file.write(
'''import sys
sys.path.append('{}')
import {}
{}'''.format(python_bind_lib_path, module_cpp_name, export_symbol_str).encode())
    sys.path.append(python_bind_lib_path)
    subprocess.run("cd {} && python -m pybind11_stubgen {} -o {}".
                   format(python_bind_lib_path, module_cpp_name, python_bind_path),
                    shell=True)