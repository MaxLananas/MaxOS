#include "screen.h"
#include "../kernel/io.h"

void v_init(void) {
    // Initialisation écran
}

void v_put(unsigned int x, unsigned int y, char c, unsigned char fg, unsigned char bg) {
    // Affichage caractère
}

void v_str(unsigned int x, unsigned int y, const char* s, unsigned char fg, unsigned char bg) {
    // Affichage chaîne
}

void v_fill(unsigned int x1, unsigned int y1, unsigned int x2, unsigned int y2, unsigned char fg, unsigned char bg) {
    // Remplissage zone
}