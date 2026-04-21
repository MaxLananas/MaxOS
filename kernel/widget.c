#include "widget.h"
#include "ui.h"

void widget_draw() {
    ui_draw_window(10, 5, 60, 15, "Terminal");
    ui_draw_button(20, 10, 10, 3, 0x0F, 0x01, "Button1");
}