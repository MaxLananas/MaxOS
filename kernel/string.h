#ifndef STRING_H
#define STRING_H

unsigned int strlen(const char *str) {
    unsigned int len = 0;
    while (str[len]) len++;
    return len;
}

#endif