#include "debug/log.h"
#include "../io.h"
#include "drivers/screen.h"

#define COM1_PORT 0x3F8

static unsigned char log_level = LOG_LEVEL_INFO;

void log_init(void) {
    outb(COM1_PORT + 1, 0x00);
    outb(COM1_PORT + 3, 0x80);
    outb(COM1_PORT + 0, 0x03);
    outb(COM1_PORT + 1, 0x00);
    outb(COM1_PORT + 3, 0x03);
    outb(COM1_PORT + 2, 0xC7);
    outb(COM1_PORT + 4, 0x0B);
}

void log_write(unsigned char level, const char *message) {
    if (level < log_level) return;

    while (*message) {
        outb(COM1_PORT, *message++);
    }
    outb(COM1_PORT, '\n');
}

void log_debug(const char *message) {
    log_write(LOG_LEVEL_DEBUG, message);
}

void log_info(const char *message) {
    log_write(LOG_LEVEL_INFO, message);
}

void log_warn(const char *message) {
    log_write(LOG_LEVEL_WARN, message);
}

void log_error(const char *message) {
    log_write(LOG_LEVEL_ERROR, message);
}