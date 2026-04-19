#ifndef TERMINAL_H
#define TERMINAL_H

#define TM_COLS 80
#define TM_OUTPUT_ROWS 25
#define TM_INPUT_ROW 24
#define TM_PROMPT_LEN 2
#define TM_START_ROW 0
#define CMD_BUFFER_SIZE 256
#define HISTORY_SIZE 10

#define KEY_F1 0x80
#define KEY_F2 0x81
#define KEY_F3 0x82
#define KEY_F4 0x83

void tm_init(void);
void tm_draw(void);
void tm_key(char k);
void tm_scroll_up(void);
void tm_print(const char* s);
void tm_print_char(char c);
void tm_execute_command(const char* cmd);
void tm_draw_input_line(void);
void tm_set_cursor(void);
void tm_beep(void);
unsigned int tm_str_len(const char* s);
int tm_str_cmp(const char* s1, const char* s2);
void tm_str_cpy(char* dest, const char* src);
void tm_str_cat(char* dest, const char* src);
void tm_mem_set(void* dest, unsigned char val, unsigned int count);
void tm_mem_cpy(void* dest, const void* src, unsigned int count);
void tm_int_to_str(unsigned int n, char* b);
void tm_int_to_str_padded(unsigned int n, char* b);
void tm_int_to_hex_str(unsigned int n, char* b);
unsigned int tm_str_to_int(const char* s);
unsigned int tm_parse_arg(const char* cmd, unsigned int arg_idx, char* buffer, unsigned int buffer_size);

#endif