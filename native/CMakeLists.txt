cmake_minimum_required(VERSION 3.11)
project(nagi_cpp) #定义工程名字
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)
include_directories(${pybind11_include_path})
include_directories(${PYTHON_INCLUDE_DIRS})
pybind11_add_module(nagi_cpp_ex test.cpp)