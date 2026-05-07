#ifndef TERMINAL_H
#define TERMINAL_H

#define MAX_CMD_LEN 256

void terminal_init(void);
void terminal_run(void);
void terminal_process(const char *cmd);

#endif