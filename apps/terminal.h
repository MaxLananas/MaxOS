#ifndef TERMINAL_H
#define TERMINAL_H

#define TM_ROWS 25
#define TM_COLS 40
#define TM_START_ROW 1
#define TM_END_ROW (TM_ROWS - 2)
#define TM_INPUT_ROW (TM_ROWS - 1)
#define TM_PROMPT_COL 0
#define TM_PROMPT_LEN 2

#define CMD_BUFFER_SIZE 128
#define HISTORY_SIZE 20

typedef unsigned int unsigned_int;
typedef int int_bool;

void tm_init(void);
void tm_draw(void);
void tm_key(char k);

unsigned_int tm_str_len(const char* s);
int tm_str_cmp(const char* s1, const char* s2);
void tm_str_cpy(char* dest, const char* src);
void tm_str_cat(char* dest, const char* src);
void tm_mem_set(void* dest, unsigned char val, unsigned_int count);
void tm_mem_cpy(void* dest, const void* src, unsigned_int count);
void tm_int_to_str(unsigned_int n, char* b);
void tm_int_to_str_padded(unsigned_int n, char* b);
void tm_int_to_hex_str(unsigned_int n, char* b);
unsigned_int tm_str_to_int(const char* s);

extern char tm_cmd_buffer[CMD_BUFFER_SIZE];
extern unsigned_int tm_cmd_buffer_len;
extern unsigned_int tm_cursor_pos;
extern char tm_history[HISTORY_SIZE][CMD_BUFFER_SIZE];
extern unsigned_int tm_history_count;
extern unsigned_int tm_history_nav_idx;
extern unsigned_int tm_current_output_row_idx;
extern unsigned_int tm_current_output_col_idx;
extern unsigned char tm_fg_color;
extern unsigned char tm_bg_color;

#define TM_OUTPUT_ROWS (TM_END_ROW - TM_START_ROW + 1)
extern char tm_output_chars[TM_OUTPUT_ROWS][TM_COLS];
extern unsigned char tm_output_attrs[TM_OUTPUT_ROWS][TM_COLS];

void tm_scroll_up(void);
void tm_print(const char* s);
void tm_print_char(char c);
void tm_execute_command(const char* cmd);
void tm_draw_input_line(void);
void tm_set_cursor(void);
void tm_beep(void);
unsigned_int tm_parse_arg(const char* cmd, unsigned_int arg_idx, char* buffer, unsigned_int buffer_size);

#endif