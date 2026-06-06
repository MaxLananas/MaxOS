#include "string.h"

unsigned int strlen(const char *str) {
    unsigned int len = 0;
    while (str[len] != '\0') {
        len++;
    }
    return len;
}

void strcpy(char *dest, const char *src) {
    unsigned int i = 0;
    while (src[i] != '\0') {
        dest[i] = src[i];
        i++;
    }
    dest[i] = '\0';
}

void strcat(char *dest, const char *src) {
    unsigned int dest_len = strlen(dest);
    unsigned int i = 0;
    while (src[i] != '\0') {
        dest[dest_len + i] = src[i];
        i++;
    }
    dest[dest_len + i] = '\0';
}