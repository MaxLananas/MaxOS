#ifndef STRING_H
#define STRING_H

unsigned int strlen(const char *str);
int strcmp(const char *str1, const char *str2);
void *memcpy(void *dest, const void *src, unsigned int n);
void *memset(void *s, int c, unsigned int n);

#endif