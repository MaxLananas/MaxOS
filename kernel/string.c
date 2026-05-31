#include "string.h"

unsigned int strlen(const char *str)
{
    unsigned int len = 0;
    while (str[len]) len++;
    return len;
}

void strcpy(char *dest, const char *src)
{
    unsigned int i = 0;
    while (src[i]) {
        dest[i] = src[i];
        i++;
    }
    dest[i] = '\0';
}

void strcat(char *dest, const char *src)
{
    unsigned int i = dest_len = strlen(dest);
    unsigned int j = 0;
    while (src[j]) {
        dest[i++] = src[j++];
    }
    dest[i] = '\0';
}