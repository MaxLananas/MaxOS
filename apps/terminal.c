#include "terminal.h"
#include "../drivers/screen.h"
#include "../drivers/keyboard.h"
#include "../kernel/io.h"

char tm_cmd_buffer[CMD_BUFFER_SIZE];
unsigned_int tm_cmd_buffer_len = 0;
unsigned_int tm_cursor_pos = 0;
char tm_history[HISTORY_SIZE][CMD_BUFFER_SIZE];
unsigned_int tm_history_count = 0;
unsigned_int tm_history_nav_idx = 0;
unsigned_int tm_current_output_row_idx = 0;
unsigned_int tm_current_output_col_idx = 0;
unsigned char tm_fg_color = 0x0F;
unsigned char tm_bg_color = 0x00;

char tm_output_chars[TM_OUTPUT_ROWS][TM_COLS];
unsigned char tm_output_attrs[TM_OUTPUT_ROWS][TM_COLS];

void tm_init(void) {
    tm_mem_set(tm_output_chars, ' ', sizeof(tm_output_chars));
    tm_mem_set(tm_output_attrs, (tm_bg_color << 4) | tm_fg_color, sizeof(tm_output_attrs));
    tm_cmd_buffer_len = 0;
    tm_cursor_pos = 0;
    tm_history_count = 0;
    tm_history_nav_idx = 0;
    tm_current_output_row_idx = 0;
    tm_current_output_col_idx = 0;
}

void tm_draw(void) {
    for (unsigned_int y = 0; y < TM_OUTPUT_ROWS; y++) {
        v_str(0, TM_START_ROW + y, tm_output_chars[y], tm_output_attrs[y][0] & 0x0F, tm_output_attrs[y][0] >> 4);
    }
    tm_draw_input_line();
    tm_set_cursor();
}

void tm_key(char k) {
    if (k == 0) return;

    if (k == '\n') {
        tm_print("\n");
        if (tm_cmd_buffer_len > 0) {
            tm_str_cpy(tm_history[tm_history_count % HISTORY_SIZE], tm_cmd_buffer);
            tm_history_count++;
            tm_history_nav_idx = tm_history_count;
            tm_execute_command(tm_cmd_buffer);
            tm_cmd_buffer_len = 0;
            tm_cursor_pos = 0;
        }
        return;
    }

    if (k == '\b') {
        if (tm_cursor_pos > 0) {
            tm_cursor_pos--;
            for (unsigned_int i = tm_cursor_pos; i < tm_cmd_buffer_len - 1; i++) {
                tm_cmd_buffer[i] = tm_cmd_buffer[i + 1];
            }
            tm_cmd_buffer_len--;
            tm_cmd_buffer[tm_cmd_buffer_len] = ' ';
        }
        return;
    }

    if (k == '\t') {
        k = ' ';
    }

    if (tm_cursor_pos < CMD_BUFFER_SIZE - 1 && k >= ' ' && k <= '~') {
        for (unsigned_int i = tm_cmd_buffer_len; i > tm_cursor_pos; i--) {
            tm_cmd_buffer[i] = tm_cmd_buffer[i - 1];
        }
        tm_cmd_buffer[tm_cursor_pos] = k;
        tm_cursor_pos++;
        if (tm_cmd_buffer_len < CMD_BUFFER_SIZE - 1) {
            tm_cmd_buffer_len++;
        }
    }
}

void tm_scroll_up(void) {
    for (unsigned_int y = 0; y < TM_OUTPUT_ROWS - 1; y++) {
        tm_mem_cpy(tm_output_chars[y], tm_output_chars[y + 1], sizeof(tm_output_chars[y]));
        tm_mem_cpy(tm_output_attrs[y], tm_output_attrs[y + 1], sizeof(tm_output_attrs[y]));
    }
    tm_mem_set(tm_output_chars[TM_OUTPUT_ROWS - 1], ' ', sizeof(tm_output_chars[TM_OUTPUT_ROWS - 1]));
    tm_mem_set(tm_output_attrs[TM_OUTPUT_ROWS - 1], (tm_bg_color << 4) | tm_fg_color, sizeof(tm_output_attrs[TM_OUTPUT_ROWS - 1]));
    if (tm_current_output_row_idx > 0) {
        tm_current_output_row_idx--;
    }
}

void tm_print(const char* s) {
    while (*s) {
        if (*s == '\n') {
            tm_current_output_col_idx = 0;
            if (tm_current_output_row_idx < TM_OUTPUT_ROWS - 1) {
                tm_current_output_row_idx++;
            } else {
                tm_scroll_up();
            }
        } else {
            if (tm_current_output_col_idx >= TM_COLS) {
                tm_current_output_col_idx = 0;
                if (tm_current_output_row_idx < TM_OUTPUT_ROWS - 1) {
                    tm_current_output_row_idx++;
                } else {
                    tm_scroll_up();
                }
            }
            tm_output_chars[tm_current_output_row_idx][tm_current_output_col_idx] = *s;
            tm_output_attrs[tm_current_output_row_idx][tm_current_output_col_idx] = (tm_bg_color << 4) | tm_fg_color;
            tm_current_output_col_idx++;
        }
        s++;
    }
}

void tm_print_char(char c) {
    if (c == '\n') {
        tm_current_output_col_idx = 0;
        if (tm_current_output_row_idx < TM_OUTPUT_ROWS - 1) {
            tm_current_output_row_idx++;
        } else {
            tm_scroll_up();
        }
    } else {
        if (tm_current_output_col_idx >= TM_COLS) {
            tm_current_output_col_idx = 0;
            if (tm_current_output_row_idx < TM_OUTPUT_ROWS - 1) {
                tm_current_output_row_idx++;
            } else {
                tm_scroll_up();
            }
        }
        tm_output_chars[tm_current_output_row_idx][tm_current_output_col_idx] = c;
        tm_output_attrs[tm_current_output_row_idx][tm_current_output_col_idx] = (tm_bg_color << 4) | tm_fg_color;
        tm_current_output_col_idx++;
    }
}

void tm_draw_input_line(void) {
    char line[TM_COLS + 1];
    unsigned_int i;

    for (i = 0; i < TM_PROMPT_LEN; i++) {
        line[i] = "> ";
    }
    for (; i < TM_COLS; i++) {
        if (i < tm_cursor_pos + TM_PROMPT_LEN) {
            line[i] = tm_cmd_buffer[i - TM_PROMPT_LEN];
        } else {
            line[i] = ' ';
        }
    }
    line[TM_COLS] = 0;

    v_str(0, TM_INPUT_ROW, line, tm_fg_color, tm_bg_color);
}

void tm_set_cursor(void) {
    unsigned_int pos = tm_cursor_pos + TM_PROMPT_LEN;
    unsigned_int x = pos % TM_COLS;
    unsigned_int y = TM_INPUT_ROW;
    v_put(x, y, ' ', tm_fg_color, tm_bg_color);
}

void tm_beep(void) {
    outb(0x43, 0xB6);
    outb(0x42, 0x04);
    outb(0x42, 0x11);
    unsigned char tmp = inb(0x61);
    if (tmp != (tmp | 0x03)) {
        outb(0x61, tmp | 0x03);
    }
    for (unsigned_int i = 0; i < 100000; i++);
    outb(0x61, tmp);
}

unsigned_int tm_str_len(const char* s) {
    unsigned_int len = 0;
    while (s[len] != 0) {
        len++;
    }
    return len;
}

int tm_str_cmp(const char* s1, const char* s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(unsigned char*)s1 - *(unsigned char*)s2;
}

void tm_str_cpy(char* dest, const char* src) {
    while ((*dest++ = *src++));
}

void tm_str_cat(char* dest, const char* src) {
    while (*dest) dest++;
    while ((*dest++ = *src++));
}

void tm_mem_set(void* dest, unsigned char val, unsigned_int count) {
    unsigned char* d = (unsigned char*)dest;
    while (count--) {
        *d++ = val;
    }
}

void tm_mem_cpy(void* dest, const void* src, unsigned_int count) {
    unsigned char* d = (unsigned char*)dest;
    const unsigned char* s = (const unsigned char*)src;
    while (count--) {
        *d++ = *s++;
    }
}

void tm_int_to_str(unsigned_int n, char* b) {
    unsigned_int i = 0;
    unsigned_int shifter = n;

    do {
        ++i;
        shifter = shifter / 10;
    } while (shifter);

    b[i] = 0;
    do {
        --i;
        b[i] = '0' + (n % 10);
        n /= 10;
    } while (n);
}

void tm_int_to_str_padded(unsigned_int n, char* b) {
    unsigned_int i = 0;
    unsigned_int shifter = n;

    do {
        ++i;
        shifter = shifter / 10;
    } while (shifter);

    while (i < 5) {
        b[i++] = '0';
    }
    b[i] = 0;
    do {
        --i;
        b[i] = '0' + (n % 10);
        n /= 10;
    } while (n);
}

void tm_int_to_hex_str(unsigned_int n, char* b) {
    const char* digits = "0123456789ABCDEF";
    unsigned_int i = 0;

    b[0] = '0';
    b[1] = 'x';
    i = 2;

    for (unsigned_int j = 0; j < 8; j++) {
        unsigned_int digit = (n >> (28 - j * 4)) & 0xF;
        b[i++] = digits[digit];
    }
    b[i] = 0;
}

unsigned_int tm_str_to_int(const char* s) {
    unsigned_int n = 0;
    while (*s >= '0' && *s <= '9') {
        n = n * 10 + (*s++ - '0');
    }
    return n;
}

unsigned_int tm_parse_arg(const char* cmd, unsigned_int arg_idx, char* buffer, unsigned_int buffer_size) {
    unsigned_int arg_count = 0;
    unsigned_int current_arg = 0;
    unsigned_int in_arg = 0;
    unsigned_int pos = 0;

    while (cmd[pos] && arg_count <= arg_idx) {
        if (cmd[pos] == ' ' || cmd[pos] == '\t') {
            if (in_arg) {
                in_arg = 0;
                current_arg++;
            }
        } else {
            if (!in_arg) {
                if (arg_count == arg_idx) {
                    unsigned_int start = pos;
                    while (cmd[pos] && cmd[pos] != ' ' && cmd[pos] != '\t') {
                        pos++;
                    }
                    unsigned_int len = pos - start;
                    if (len >= buffer_size) {
                        len = buffer_size - 1;
                    }
                    tm_mem_cpy(buffer, cmd + start, len);
                    buffer[len] = 0;
                    return len;
                }
                in_arg = 1;
            }
        }
        pos++;
    }
    return 0;
}

void tm_execute_command(const char* cmd) {
    char buffer[32];

    if (tm_str_cmp(cmd, "help") == 0) {
        tm_print("Commandes disponibles:\n");
        tm_print("  help - Affiche cette aide\n");
        tm_print("  clear - Efface l'ecran\n");
        tm_print("  reboot - Redemarre le systeme\n");
        tm_print("  echo <texte> - Affiche du texte\n");
        tm_print("  beep - Emet un bip\n");
    }
    else if (tm_str_cmp(cmd, "clear") == 0) {
        tm_mem_set(tm_output_chars, ' ', sizeof(tm_output_chars));
        tm_mem_set(tm_output_attrs, (tm_bg_color << 4) | tm_fg_color, sizeof(tm_output_attrs));
        tm_current_output_row_idx = 0;
        tm_current_output_col_idx = 0;
    }
    else if (tm_str_cmp(cmd, "reboot") == 0) {
        outb(0x64, 0xFE);
    }
    else if (tm_str_cmp(cmd, "echo") == 0) {
        unsigned_int len = tm_parse_arg(cmd, 1, buffer, sizeof(buffer));
        if (len > 0) {
            tm_print(buffer);
            tm_print("\n");
        } else {
            tm_print("Usage: echo <texte>\n");
        }
    }
    else if (tm_str_cmp(cmd, "beep") == 0) {
        tm_beep();
    }
    else if (tm_str_len(cmd) > 0) {
        tm_print("Commande inconnue: ");
        tm_print(cmd);
        tm_print("\n");
    }
}