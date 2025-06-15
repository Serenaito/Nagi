#include <pybind11/pybind11.h>


class LAppWindow 
{
public:
    LAppWindow(){}

    LAppWindow(pybind11::object _obj)
    {
        obj = _obj;
    }

    int height() 
    {
        return pybind11::int_(obj.attr("height")());
    }

    int width()
    {
        return pybind11::int_(obj.attr("width")());
    }

private:
    pybind11::object obj;
};