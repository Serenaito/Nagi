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

void model_cick_press(int x, int y)
{
    LAppDelegate::GetInstance()->mousePressEvent(x, y);
}

void model_cick_move(int x, int y)
{
    LAppDelegate::GetInstance()->mouseMoveEvent(x, y);
}

void model_cick_release(int x, int y)
{
    LAppDelegate::GetInstance()->mouseReleaseEvent(x, y);
}


PYBIND11_MODULE(nagi_cpp_ex, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring
    m.def("model_init", &model_init, "model_init");
    m.def("model_resize", &model_resize, "model_resize");
    m.def("model_update", &model_update, "model_update");
    m.def("model_cick_press", &model_cick_press, "model_cick_press");
    m.def("model_cick_move", &model_cick_move, "model_cick_move");
    m.def("model_cick_release", &model_cick_release, "model_cick_release");
}