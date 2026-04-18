#include "memory.h"

// Calcul des paramètres de la bitmap
#define TOTAL_MANAGED_MEMORY (MEM_END_ADDRESS - MEM_START_ADDRESS)
#define TOTAL_PAGES          (TOTAL_MANAGED_MEMORY / PAGE_SIZE)
#define BITMAP_SIZE_BYTES    (TOTAL_PAGES / 8)

// Bitmap pour suivre l'état des pages (1 bit par page)
// Stockée dans la section .bss du kernel, donc hors de la zone gérée (1MB-16MB)
static unsigned char memory_bitmap[BITMAP_SIZE_BYTES];

// Fonction utilitaire pour marquer un bit comme utilisé
static void set_bit(unsigned int bit_index) {
    unsigned int byte_index = bit_index / 8;
    unsigned int bit_offset = bit_index % 8;
    if (byte_index < BITMAP_SIZE_BYTES) {
        memory_bitmap[byte_index] |= (1 << bit_offset);
    }
}

// Fonction utilitaire pour marquer un bit comme libre
static void clear_bit(unsigned int bit_index) {
    unsigned int byte_index = bit_index / 8;
    unsigned int bit_offset = bit_index % 8;
    if (byte_index < BITMAP_SIZE_BYTES) {
        memory_bitmap[byte_index] &= ~(1 << bit_offset);
    }
}

// Fonction utilitaire pour tester l'état d'un bit
static int test_bit(unsigned int bit_index) {
    unsigned int byte_index = bit_index / 8;
    unsigned int bit_offset = bit_index % 8;
    if (byte_index < BITMAP_SIZE_BYTES) {
        return (memory_bitmap[byte_index] >> bit_offset) & 1;
    }
    return 0; // Hors limites, considérer comme libre ou erreur
}

// Initialise le gestionnaire de mémoire
void mem_init(void) {
    unsigned int i;
    // Initialise tous les bits de la bitmap à 0 (toutes les pages sont libres)
    for (i = 0; i < BITMAP_SIZE_BYTES; i++) {
        memory_bitmap[i] = 0;
    }
    // Le kernel et la bitmap sont supposés être chargés avant MEM_START_ADDRESS (1MB).
    // Donc, aucune page de la zone 1MB-16MB n'est initialement marquée comme utilisée par le kernel.
}

// Alloue une page physique de 4KB
// Retourne l'adresse physique de la page allouée ou 0 si aucune page n'est disponible
void* mem_alloc(void) {
    unsigned int i;
    for (i = 0; i < TOTAL_PAGES; i++) {
        if (!test_bit(i)) { // Trouve la première page libre
            set_bit(i); // Marque la page comme utilisée
            // Calcule l'adresse physique de la page
            return (void*)(MEM_START_ADDRESS + (i * PAGE_SIZE));
        }
    }
    return (void*)0; // Aucune page libre trouvée
}

// Libère une page physique précédemment allouée
void mem_free(void* ptr) {
    if (ptr == (void*)0) { // Vérifie si le pointeur est valide (non NULL)
        return;
    }
    unsigned int address = (unsigned int)ptr;

    // Vérifie si l'adresse est dans la plage gérée et est alignée sur une page
    if (address < MEM_START_ADDRESS || address >= MEM_END_ADDRESS || (address % PAGE_SIZE) != 0) {
        // Adresse invalide pour la libération
        return;
    }

    // Calcule l'index de la page correspondant à l'adresse
    unsigned int page_index = (address - MEM_START_ADDRESS) / PAGE_SIZE;

    if (page_index < TOTAL_PAGES) {
        clear_bit(page_index); // Marque la page comme libre
    }
}

// Retourne la quantité de mémoire utilisée en KB
unsigned int mem_used_kb(void) {
    unsigned int used_pages = 0;
    unsigned int i;
    for (i = 0; i < TOTAL_PAGES; i++) {
        if (test_bit(i)) {
            used_pages++;
        }
    }
    return used_pages * (PAGE_SIZE / 1024); // Convertit le nombre de pages utilisées en KB
}

// Retourne la quantité totale de mémoire gérée en KB
unsigned int mem_total_kb(void) {
    return TOTAL_PAGES * (PAGE_SIZE / 1024); // Convertit le nombre total de pages en KB
}