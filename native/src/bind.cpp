#include <pybind11/pybind11.h>
#include <iostream>
#include "LAppDelegate.hpp"
#include "LAppLive2DManager.hpp"
#include "LAppModel.hpp"
void model_init(pybind11::object obj)
{
    LAppDelegate::GetInstance()->Initialize(std::move(LAppWindow(obj)));
}

void model_resize(int w, int h)
{
    LAppDelegate::GetInstance()->resize(w, h);
}

void module_init(std::string str)
{
    LAppLive2DManager::GetInstance()->ChangeScene(const_cast<char*>(str.c_str()));
}

void model_update()
{
    LAppDelegate::GetInstance()->update();
}

PYBIND11_MODULE(nagi_cpp_ex, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("model_init", &model_init, "model_init");
    m.def("model_resize", &model_resize, "model_resize");
    m.def("model_update", &model_update, "model_update");
}