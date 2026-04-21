#include "ui.h"
#include "screen.h"

void ui_draw_button(unsigned int x, unsigned int y, unsigned int width, unsigned int height, unsigned char fg, unsigned char bg, const char *text) {
    unsigned int i, j;
    unsigned char *vidmem = (unsigned char*)0xB8000;

    for (i = y; i < y + height; i++) {
        for (j = x; j < x + width; j++) {
            unsigned int pos = i * 80 + j;
            if (i == y || i == y + height - 1 || j == x || j == x + width - 1) {
                vidmem[pos * 2] = ' ';
                vidmem[pos * 2 + 1] = (fg & 0x0F) | ((bg & 0x0F) << 4);
            } else {
                vidmem[pos * 2] = ' ';
                vidmem[pos * 2 + 1] = (fg & 0x0F) | ((bg & 0x0F) << 4);
            }
        }
    }

    unsigned int text_len = 0;
    while (text[text_len]) text_len++;

    unsigned int text_x = x + (width - text_len) / 2;
    unsigned int text_y = y + height / 2;

    for (i = 0; i < text_len; i++) {
        unsigned int pos = text_y * 80 + text_x + i;
        vidmem[pos * 2] = text[i];
        vidmem[pos * 2 + 1] = (fg & 0x0F) | ((bg & 0x0F) << 4);
    }
}

void ui_draw_window(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char *title) {
    unsigned int i, j;
    unsigned char *vidmem = (unsigned char*)0xB8000;

    for (i = y; i < y + height; i++) {
        for (j = x; j < x + width; j++) {
            unsigned int pos = i * 80 + j;
            if (i == y || i == y + height - 1 || j == x || j == x + width - 1) {
                vidmem[pos * 2] = ' ';
                vidmem[pos * 2 + 1] = 0x0F;
            } else if (i == y + 1 && j > x + 1 && j < x + width - 2) {
                unsigned int title_len = 0;
                while (title[title_len]) title_len++;
                unsigned int title_x = x + (width - title_len) / 2;
                if (j >= title_x && j < title_x + title_len) {
                    vidmem[pos * 2] = title[j - title_x];
                    vidmem[pos * 2 + 1] = 0x0F;
                } else {
                    vidmem[pos * 2] = ' ';
                    vidmem[pos * 2 + 1] = 0x0F;
                }
            } else {
                vidmem[pos * 2] = ' ';
                vidmem[pos * 2 + 1] = 0x07;
            }
        }
    }
}