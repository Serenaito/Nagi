#include "Platform.hpp"
#include <Windows.h>
#include <dwmapi.h>

void PlatformLibrary::set_background_transparent(int handle)
{
    DWM_BLURBEHIND bb = { 0 };
    HRGN hRgn = CreateRectRgn(0, 0, -1, -1);
    bb.dwFlags = DWM_BB_ENABLE | DWM_BB_BLURREGION;
    bb.hRgnBlur = hRgn;
    bb.fEnable = TRUE;
    DwmEnableBlurBehindWindow(HWND(handle), &bb);
}