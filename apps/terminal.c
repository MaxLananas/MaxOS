#include "terminal.h"
#include "../drivers/keyboard.h"
#include "../kernel/io.h"

char tm_cmd_buffer[CMD_BUFFER_SIZE];
unsigned int tm_cmd_buffer_len = 0;
unsigned int tm_cursor_pos = 0;
char tm_history[HISTORY_SIZE][CMD_BUFFER_SIZE];
unsigned int tm_history_count = 0;
unsigned int tm_history_nav_idx = 0;
unsigned int tm_current_output_row_idx = 0;
unsigned int tm_current_output_col_idx = 0;
unsigned char tm_fg_color = 0x0F;
unsigned char tm_bg_color = 0x00;

char tm_output_chars[TM_OUTPUT_ROWS][TM_COLS];
unsigned char tm_output_attrs[TM_OUTPUT_ROWS][TM_COLS];

void tm_init(void) {
    unsigned int i, j;
    for (i = 0; i < TM_OUTPUT_ROWS; i++) {
        for (j = 0; j < TM_COLS; j++) {
            tm_output_chars[i][j] = ' ';
            tm_output_attrs[i][j] = tm_fg_color | (tm_bg_color << 4);
        }
    }
    tm_cmd_buffer_len = 0;
    tm_cursor_pos = 0;
    tm_history_count = 0;
    tm_history_nav_idx = 0;
    tm_current_output_row_idx = 0;
    tm_current_output_col_idx = 0;
}

void tm_draw(void) {
    unsigned int row, col;
    for (row = 0; row < TM_OUTPUT_ROWS; row++) {
        for (col = 0; col < TM_COLS; col++) {
            unsigned short pos = (TM_START_ROW + row) * 80 + col;
            unsigned short val = tm_output_chars[row][col] | (tm_output_attrs[row][col] << 8);
            outw(0x3D4, 0x0F);
            outw(0x3D5, pos & 0xFF);
            outw(0x3D4, 0x0E);
            outw(0x3D5, (pos >> 8) & 0xFF);
            outw(0x3D4, 0x0C);
            outw(0x3D5, (pos >> 8) & 0xFF);
            outw(0x3D4, 0x0D);
            outw(0x3D5, pos & 0xFF);
            outw(0x3D4, 0x0E);
            outw(0x3D5, (pos >> 8) & 0xFF);
        }
    }
}

void tm_key(char k) {
    if (k == '\b') {
        if (tm_cmd_buffer_len > 0) {
            tm_cmd_buffer_len--;
            tm_cursor_pos--;
            if (tm_cursor_pos < TM_PROMPT_LEN) tm_cursor_pos = TM_PROMPT_LEN;
            tm_output_chars[TM_INPUT_ROW][tm_cursor_pos] = ' ';
            tm_output_attrs[TM_INPUT_ROW][tm_cursor_pos] = tm_fg_color | (tm_bg_color << 4);
        }
    } else if (k == '\n') {
        tm_execute_command(tm_cmd_buffer);
        tm_cmd_buffer_len = 0;
        tm_cursor_pos = TM_PROMPT_LEN;
    } else if (k == '\t') {
        if (tm_cmd_buffer_len < CMD_BUFFER_SIZE - 1) {
            tm_cmd_buffer[tm_cmd_buffer_len++] = ' ';
            tm_cursor_pos++;
        }
    } else if (k >= KEY_F1 && k <= KEY_F4) {
        switch (k) {
            case KEY_F1:
                tm_print("Help: Available commands: clear, help, reboot\n");
                break;
            case KEY_F2:
                tm_scroll_up();
                break;
            case KEY_F3:
                tm_print("System info: Bare metal x86 OS\n");
                break;
            case KEY_F4:
                outb(0x64, 0xFE);
                break;
        }
    } else if (k >= 32 && k <= 126) {
        if (tm_cmd_buffer_len < CMD_BUFFER_SIZE - 1) {
            if (tm_cursor_pos < TM_COLS - 1) {
                tm_mem_cpy(&tm_cmd_buffer[tm_cursor_pos - TM_PROMPT_LEN], &tm_cmd_buffer[tm_cursor_pos - TM_PROMPT_LEN + 1], tm_cmd_buffer_len - (tm_cursor_pos - TM_PROMPT_LEN));
                tm_cmd_buffer[tm_cursor_pos - TM_PROMPT_LEN] = k;
                tm_cmd_buffer_len++;
                tm_cursor_pos++;
            }
        }
    }
    tm_draw_input_line();
}

void tm_scroll_up(void) {
    unsigned int i, j;
    for (i = 1; i < TM_OUTPUT_ROWS; i++) {
        for (j = 0; j < TM_COLS; j++) {
            tm_output_chars[i-1][j] = tm_output_chars[i][j];
            tm_output_attrs[i-1][j] = tm_output_attrs[i][j];
        }
    }
    for (j = 0; j < TM_COLS; j++) {
        tm_output_chars[TM_OUTPUT_ROWS-1][j] = ' ';
        tm_output_attrs[TM_OUTPUT_ROWS-1][j] = tm_fg_color | (tm_bg_color << 4);
    }
}

void tm_print(const char* s) {
    unsigned int i = 0;
    while (s[i]) {
        tm_print_char(s[i]);
        i++;
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
        tm_output_attrs[tm_current_output_row_idx][tm_current_output_col_idx] = tm_fg_color | (tm_bg_color << 4);
        tm_current_output_col_idx++;
    }
}

void tm_execute_command(const char* cmd) {
    if (tm_str_cmp(cmd, "clear") == 0) {
        unsigned int i, j;
        for (i = 0; i < TM_OUTPUT_ROWS; i++) {
            for (j = 0; j < TM_COLS; j++) {
                tm_output_chars[i][j] = ' ';
            }
        }
        tm_print("> ");
    } else if (tm_str_cmp(cmd, "help") == 0) {
        tm_print("Available commands:\n");
        tm_print("  clear - Clear the screen\n");
        tm_print("  help - Show this help\n");
        tm_print("  reboot - Reboot the system\n");
        tm_print("  info - Show system information\n");
    } else if (tm_str_cmp(cmd, "reboot") == 0) {
        outb(0x64, 0xFE);
    } else if (tm_str_len(cmd) > 0) {
        tm_print("Unknown command: ");
        tm_print(cmd);
        tm_print("\n");
    } else {
        tm_print("> ");
    }
}

void tm_draw_input_line(void) {
    unsigned int i;
    for (i = 0; i < TM_COLS; i++) {
        if (i < TM_PROMPT_LEN) {
            tm_output_chars[TM_INPUT_ROW][i] = '>';
        } else if (i - TM_PROMPT_LEN < tm_cmd_buffer_len) {
            tm_output_chars[TM_INPUT_ROW][i] = tm_cmd_buffer[i - TM_PROMPT_LEN];
        } else {
            tm_output_chars[TM_INPUT_ROW][i] = ' ';
        }
        tm_output_attrs[TM_INPUT_ROW][i] = tm_fg_color | (tm_bg_color << 4);
    }
}

void tm_set_cursor(void) {
    unsigned int pos = (TM_INPUT_ROW * TM_COLS) + tm_cursor_pos;
    outb(0x3D4, 0x0F);
    outb(0x3D5, pos & 0xFF);
    outb(0x3D4, 0x0E);
    outb(0x3D5, (pos >> 8) & 0xFF);
}

void tm_beep(void) {
    outb(0x43, 0xB6);
    outb(0x42, 0x00);
    outb(0x42, 0x00);
    unsigned char tmp = inb(0x61);
    if (tmp != (tmp | 3)) {
        outb(0x61, tmp | 3);
    }
    for (unsigned int i = 0; i < 100000; i++);
    outb(0x61, tmp);
}

unsigned int tm_str_len(const char* s) {
    unsigned int len = 0;
    while (s[len]) len++;
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

void tm_mem_set(void* dest, unsigned char val, unsigned int count) {
    unsigned char* tmp = (unsigned char*)dest;
    for (; count != 0; count--) *tmp++ = val;
}

void tm_mem_cpy(void* dest, const void* src, unsigned int count) {
    const unsigned char* sp = (const unsigned char*)src;
    unsigned char* dp = (unsigned char*)dest;
    for (; count != 0; count--) *dp++ = *sp++;
}

void tm_int_to_str(unsigned int n, char* b) {
    unsigned int i = 0;
    do {
        b[i++] = n % 10 + '0';
    } while (n /= 10);
    b[i] = '\0';
}

void tm_int_to_str_padded(unsigned int n, char* b) {
    unsigned int i = 0;
    do {
        b[i++] = n % 10 + '0';
    } while (n /= 10);
    while (i < 5) b[i++] = ' ';
    b[i] = '\0';
}

void tm_int_to_hex_str(unsigned int n, char* b) {
    unsigned int i = 0;
    unsigned int j;
    do {
        unsigned int digit = n % 16;
        b[i++] = (digit < 10) ? (digit + '0') : (digit - 10 + 'A');
    } while (n /= 16);
    for (j = i; j < 8; j++) b[j] = ' ';
    b[8] = '\0';
}

unsigned int tm_str_to_int(const char* s) {
    unsigned int n = 0;
    while (*s >= '0' && *s <= '9') {
        n = n * 10 + (*s++ - '0');
    }
    return n;
}

unsigned int tm_parse_arg(const char* cmd, unsigned int arg_idx, char* buffer, unsigned int buffer_size) {
    unsigned int arg_count = 0;
    unsigned int in_arg = 0;
    unsigned int arg_start = 0;
    unsigned int i = 0;

    while (cmd[i]) {
        if (cmd[i] == ' ' || cmd[i] == '\t') {
            if (in_arg) {
                in_arg = 0;
                if (arg_count == arg_idx) {
                    unsigned int len = i - arg_start;
                    if (len >= buffer_size) len = buffer_size - 1;
                    tm_mem_cpy(buffer, &cmd[arg_start], len);
                    buffer[len] = '\0';
                    return len;
                }
                arg_count++;
            }
        } else if (!in_arg) {
            in_arg = 1;
            arg_start = i;
        }
        i++;
    }

    if (in_arg && arg_count == arg_idx) {
        unsigned int len = i - arg_start;
        if (len >= buffer_size) len = buffer_size - 1;
        tm_mem_cpy(buffer, &cmd[arg_start], len);
        buffer[len] = '\0';
        return len;
    }

    return 0;
}