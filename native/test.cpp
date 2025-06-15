#include <pybind11/pybind11.h>
#include <iostream>


int add(int i, int j) {
    return i + j;
}
PYBIND11_MODULE(nagi_cpp_ex, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("add", &add, "A function which adds two numbers");
}