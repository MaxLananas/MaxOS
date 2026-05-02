#include "string.h"

unsigned int strlen(const char *str) {
    unsigned int len = 0;
    while (str[len]) len++;
    return len;
}

void strcpy(char *dest, const char *src) {
    unsigned int i = 0;
    while ((dest[i] = src[i])) i++;
}

void strcat(char *dest, const char *src) {
    unsigned int i = strlen(dest);
    unsigned int j = 0;
    while ((dest[i++] = src[j++]));
}