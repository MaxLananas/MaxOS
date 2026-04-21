static unsigned char *video_memory = (unsigned char*)0xB8000;
static unsigned int cursor_x = 0;
static unsigned int cursor_y = 0;
static unsigned char current_color = 0x0F;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned int i;
    for (i = 0; i < 80 * 25 * 2; i += 2) {
        video_memory[i] = ' ';
        video_memory[i+1] = current_color;
    }
    cursor_x = 0;
    cursor_y = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        cursor_y++;
        cursor_x = 0;
    } else {
        unsigned int index = (cursor_y * 80 + cursor_x) * 2;
        video_memory[index] = c;
        video_memory[index+1] = color;
        cursor_x++;
    }

    if (cursor_x >= 80) {
        cursor_x = 0;
        cursor_y++;
    }

    if (cursor_y >= 25) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char color) {
    unsigned int i = 0;
    while (str[i]) {
        screen_putchar(str[i], color);
        i++;
    }
}

void screen_writeln(const char *str, unsigned char color) {
    screen_write(str, color);
    screen_putchar('\n', color);
}

void screen_set_color(unsigned char color) {
    current_color = color;
}

int screen_get_row(void) {
    return cursor_y;
}

void screen_scroll(void) {
    unsigned int i;
    for (i = 0; i < 24 * 80 * 2; i++) {
        video_memory[i] = video_memory[i + 80 * 2];
    }
    for (i = 24 * 80 * 2; i < 25 * 80 * 2; i += 2) {
        video_memory[i] = ' ';
        video_memory[i+1] = current_color;
    }
    cursor_y = 24;
}