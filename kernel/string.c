#include "string.h"

unsigned int strlen(const char *str) {
    unsigned int len = 0;
    while (str[len]) len++;
    return len;
}

int strcmp(const char *str1, const char *str2) {
    while (*str1 && (*str1 == *str2)) {
        str1++;
        str2++;
    }
    return *(unsigned char *)str1 - *(unsigned char *)str2;
}