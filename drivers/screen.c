#include "screen.h"

void v_init(void) {
}

void v_fill(unsigned int r1, unsigned int c1, unsigned int r2, unsigned int c2, unsigned char fg, unsigned char bg) {
    (void)r1; (void)c1; (void)r2; (void)c2; (void)fg; (void)bg;
}

void v_str(unsigned int r, unsigned int c, const char* str, unsigned char fg, unsigned char bg) {
    (void)r; (void)c; (void)str; (void)fg; (void)bg;
}

void v_put(unsigned int r, unsigned int c, char ch, unsigned char fg, unsigned char bg) {
    (void)r; (void)c; (void)ch; (void)fg; (void)bg;
}