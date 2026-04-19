void ui_init() {
    v_fill(0, 0, 80, 25, ' ', 0x07);
}

void ui_topbar() {
    v_fill(0, 0, 80, 1, ' ', 0x70);
    v_str(1, 0, "MaxOS", 0x00, 0x70);
}

void ui_taskbar() {
    v_fill(0, 24, 80, 1, ' ', 0x70);
}

void ui_draw_window(unsigned int x, unsigned int y, unsigned int w, unsigned int h, const char* title) {
    v_fill(x, y, w, h, ' ', 0x1F);
    v_str(x+2, y, title, 0x0F, 0x1F);
}

void ui_draw_button(unsigned int x, unsigned int y, unsigned int w, unsigned int h, const char* text) {
    v_fill(x, y, w, h, ' ', 0x3F);
    v_str(x+1, y, text, 0x0F, 0x3F);
}

void ui_draw_menu(unsigned int x, unsigned int y, unsigned int w, unsigned int h) {
    v_fill(x, y, w, h, ' ', 0x5F);
}