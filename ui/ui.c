#include "ui.h"
#include "../drivers/screen.h"
#include "../drivers/keyboard.h"
#include "../kernel/io.h"

#define UI_DESKTOP_COLOR 0x1F
#define UI_WINDOW_COLOR 0x3F
#define UI_BUTTON_COLOR 0x4F
#define UI_TEXT_COLOR 0x0F
#define UI_TITLE_COLOR 0x70

void ui_init(void) {
    v_fill(0, 0, 80, 25, ' ', UI_DESKTOP_COLOR);
    ui_draw_desktop();
}

void ui_topbar(int active) {
    (void)active;
    v_fill(0, 0, 80, 1, ' ', 0x70);
    v_str(1, 0, "MaxOS", 0x00, 0x70);
}

void ui_taskbar(int active) {
    (void)active;
    v_fill(0, 24, 80, 1, ' ', 0x70);
    v_str(1, 24, "F1:Menu F2:Terminal F3:Notepad F4:SysInfo F5:About", 0x00, 0x70);
}

void ui_draw_window(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* title) {
    unsigned int i;

    v_fill(x, y, width, height, ' ', UI_WINDOW_COLOR);

    for(i = x; i < x + width; i++) {
        v_put(i, y, 0xC4, UI_WINDOW_COLOR, UI_WINDOW_COLOR);
        v_put(i, y + height - 1, 0xC4, UI_WINDOW_COLOR, UI_WINDOW_COLOR);
    }

    for(i = y; i < y + height; i++) {
        v_put(x, i, 0xB3, UI_WINDOW_COLOR, UI_WINDOW_COLOR);
        v_put(x + width - 1, i, 0xB3, UI_WINDOW_COLOR, UI_WINDOW_COLOR);
    }

    v_put(x, y, 0xDA, UI_WINDOW_COLOR, UI_WINDOW_COLOR);
    v_put(x + width - 1, y, 0xBF, UI_WINDOW_COLOR, UI_WINDOW_COLOR);
    v_put(x, y + height - 1, 0xC0, UI_WINDOW_COLOR, UI_WINDOW_COLOR);
    v_put(x + width - 1, y + height - 1, 0xD9, UI_WINDOW_COLOR, UI_WINDOW_COLOR);

    v_str(x + 2, y, title, UI_TEXT_COLOR, UI_WINDOW_COLOR);
}

void ui_draw_button(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* text) {
    unsigned int text_len = 0;
    unsigned int i;

    while(text[text_len] != 0) text_len++;

    v_fill(x, y, width, height, ' ', UI_BUTTON_COLOR);

    for(i = x; i < x + width; i++) {
        v_put(i, y, 0xC4, UI_BUTTON_COLOR, UI_BUTTON_COLOR);
        v_put(i, y + height - 1, 0xC4, UI_BUTTON_COLOR, UI_BUTTON_COLOR);
    }

    for(i = y; i < y + height; i++) {
        v_put(x, i, 0xB3, UI_BUTTON_COLOR, UI_BUTTON_COLOR);
        v_put(x + width - 1, i, 0xB3, UI_BUTTON_COLOR, UI_BUTTON_COLOR);
    }

    v_put(x, y, 0xDA, UI_BUTTON_COLOR, UI_BUTTON_COLOR);
    v_put(x + width - 1, y, 0xBF, UI_BUTTON_COLOR, UI_BUTTON_COLOR);
    v_put(x, y + height - 1, 0xC0, UI_BUTTON_COLOR, UI_BUTTON_COLOR);
    v_put(x + width - 1, y + height - 1, 0xD9, UI_BUTTON_COLOR, UI_BUTTON_COLOR);

    v_str(x + (width - text_len) / 2, y + 1, text, UI_TEXT_COLOR, UI_BUTTON_COLOR);
}

void ui_draw_menu(unsigned int x, unsigned int y, const char** items, unsigned int count) {
    unsigned int i;
    unsigned int max_len = 0;

    for(i = 0; i < count; i++) {
        unsigned int len = 0;
        while(items[i][len] != 0) len++;
        if(len > max_len) max_len = len;
    }

    v_fill(x, y, max_len + 2, count + 2, ' ', 0x70);

    for(i = 0; i < count; i++) {
        v_str(x + 1, y + 1 + i, items[i], 0x00, 0x70);
    }

    for(i = x; i < x + max_len + 2; i++) {
        v_put(i, y, 0xC4, 0x70, 0x70);
        v_put(i, y + count + 1, 0xC4, 0x70, 0x70);
    }

    for(i = y; i < y + count + 2; i++) {
        v_put(x, i, 0xB3, 0x70, 0x70);
        v_put(x + max_len + 1, i, 0xB3, 0x70, 0x70);
    }

    v_put(x, y, 0xDA, 0x70, 0x70);
    v_put(x + max_len + 1, y, 0xBF, 0x70, 0x70);
    v_put(x, y + count + 1, 0xC0, 0x70, 0x70);
    v_put(x + max_len + 1, y + count + 1, 0xD9, 0x70, 0x70);
}

void ui_draw_terminal(unsigned int x, unsigned int y, unsigned int width, unsigned int height) {
    ui_draw_window(x, y, width, height, "Terminal");
}

void ui_draw_desktop(void) {
    ui_topbar(1);
    ui_taskbar(1);
}