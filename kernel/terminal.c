#include "apps/terminal.h"
#include "drivers/screen.h"
#include "drivers/keyboard.h"
#include "kernel/timer.h"
#include "kernel/memory.h"

#define CMD_MAX   256
#define HIST_SIZE 16

static char history[HIST_SIZE][CMD_MAX];
static int  hist_count = 0;
static int  hist_pos   = 0;

static void str_copy(char *dst, const char *src, int max) {
    int i = 0;
    while (src[i] && i < max - 1) { dst[i] = src[i]; i++; }
    dst[i] = 0;
}

static int str_cmp(const char *a, const char *b) {
    while (*a && *b && *a == *b) { a++; b++; }
    return *a - *b;
}

static int str_len(const char *s) {
    int n = 0;
    while (s[n]) n++;
    return n;
}

static void str_int(unsigned int n, char *buf) {
    int i = 0, j;
    char tmp[12];
    if (n == 0) { buf[0]='0'; buf[1]=0; return; }
    while (n) { tmp[i++] = '0' + (n % 10); n /= 10; }
    for (j = 0; j < i; j++) buf[j] = tmp[i - 1 - j];
    buf[i] = 0;
}

void terminal_process(const char *cmd) {
    char buf[32];
    if (str_len(cmd) == 0) return;
    if (str_cmp(cmd, "help") == 0) {
        screen_writeln("Commands: help clear uptime mem reboot", 0x0B);
    } else if (str_cmp(cmd, "clear") == 0) {
        screen_clear();
    } else if (str_cmp(cmd, "uptime") == 0) {
        unsigned int t = timer_get_ticks();
        str_int(t / 100, buf);
        screen_write("Uptime: ", 0x07);
        screen_write(buf, 0x0A);
        screen_writeln("s", 0x07);
    } else if (str_cmp(cmd, "mem") == 0) {
        str_int(mem_used_pages(), buf);
        screen_write("Used pages: ", 0x07);
        screen_write(buf, 0x0A);
        screen_writeln("", 0x07);
    } else if (str_cmp(cmd, "reboot") == 0) {
        outb_reboot:
        __asm__ volatile(
            "mov $0x64, %%dx\n"
            "mov $0xFE, %%al\n"
            "outb %%al, %%dx\n"
            :: : "eax", "edx"
        );
    } else {
        screen_write("Unknown: ", 0x0C);
        screen_writeln(cmd, 0x0C);
    }
}

void terminal_init(void) {
    screen_clear();
    screen_writeln("MaxOS v1.0 — Type 'help'", 0x0A);
    screen_write("> ", 0x0E);
}

void terminal_run(void) {
    char cmd[CMD_MAX];
    int  pos = 0;
    char c;

    while (1) {
        c = keyboard_getchar();
        if (c == '\n') {
            cmd[pos] = 0;
            screen_putchar('\n', 0x07);
            if (pos > 0) {
                str_copy(history[hist_count % HIST_SIZE], cmd, CMD_MAX);
                hist_count++;
            }
            terminal_process(cmd);
            pos = 0;
            hist_pos = hist_count;
            screen_write("> ", 0x0E);
        } else if (c == '\b') {
            if (pos > 0) {
                pos--;
                screen_putchar('\b', 0x07);
            }
        } else if (pos < CMD_MAX - 1) {
            cmd[pos++] = c;
            screen_putchar(c, 0x07);
        }
    }
}
