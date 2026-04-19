unsigned char terminal_buffer[2048];
unsigned int terminal_pos;

void terminal_init(void) {
    terminal_pos = 0;
}

void terminal_putchar(unsigned char c) {
    if (c == '\n' || terminal_pos >= 2048) {
        terminal_pos = 0;
    } else {
        terminal_buffer[terminal_pos++] = c;
    }
}