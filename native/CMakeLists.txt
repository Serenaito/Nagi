cmake_minimum_required(VERSION 3.11)
project(nagi_cpp) #定义工程名字
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)
find_package(OpenGL REQUIRED)

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
cmake_policy(SET CMP0079 NEW)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(GLFW_INSTALL OFF CACHE BOOL "" FORCE)
set(BUILD_UTILS OFF CACHE BOOL "" FORCE)
add_library(Live2DCubismCore STATIC IMPORTED)
set(CRT MT)
set_target_properties(Live2DCubismCore
  PROPERTIES
    IMPORTED_LOCATION_DEBUG
    ${CMAKE_CURRENT_SOURCE_DIR}/third/live2d/lib/Live2DCubismCore_${CRT}d.lib
    IMPORTED_LOCATION_RELEASE
    ${CMAKE_CURRENT_SOURCE_DIR}/third/live2d/lib/Live2DCubismCore_${CRT}.lib
    INTERFACE_INCLUDE_DIRECTORIES
    ${CMAKE_CURRENT_SOURCE_DIR}/third/live2d/inc/
)

set(GLEW_PATH ${CMAKE_CURRENT_SOURCE_DIR}/third/glew)
set(GLFW_PATH ${CMAKE_CURRENT_SOURCE_DIR}/third/glfw)
add_subdirectory(${GLEW_PATH}/build/cmake)
set(FRAMEWORK_SOURCE OpenGL)
add_subdirectory(framework)
target_compile_definitions(framework PUBLIC CSM_TARGET_WIN_GL)
target_include_directories(framework PUBLIC ${GLEW_PATH}/include)
target_link_libraries(framework Live2DCubismCore glew_s)

include_directories(${pybind11_INCLUDE_DIRS})
include_directories(${PYTHON_INCLUDE_DIRS})

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${GLEW_PATH}/include)
include_directories(${GLFW_PATH}/include)
include_directories(framework/src)
include_directories(third/stb)
aux_source_directory(src MY_SOURCES)
Python_add_library(nagi_cpp_ex ${MY_SOURCES})
target_compile_definitions(nagi_cpp_ex PUBLIC CSM_TARGET_WIN_GL)
target_link_libraries(nagi_cpp_ex PUBLIC pybind11::headers OpenGL::GL framework Live2DCubismCore glew_s winmm.lib
debug -NODEFAULTLIB:libcmtd.lib
optimized -NODEFAULTLIB:libcmt.lib)
target_include_directories(nagi_cpp_ex PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/third/live2d/inc)
target_include_directories(nagi_cpp_ex PUBLIC ${GLEW_PATH}/include)
target_include_directories(nagi_cpp_ex PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
set_target_properties(nagi_cpp_ex PROPERTIES
                                INTERPROCEDURAL_OPTIMIZATION ON
                                CXX_VISIBILITY_PRESET ON
                                VISIBILITY_INLINES_HIDDEN ON)
