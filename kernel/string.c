#include "string.h"

unsigned int strlen(const char *str) {
    unsigned int len = 0;
    while (str[len]) {
        len++;
    }
    return len;
}

void strcpy(char *dest, const char *src) {
    while ((*dest++ = *src++));
}

void strcat(char *dest, const char *src) {
    while (*dest) {
        dest++;
    }
    while ((*dest++ = *src++));
}