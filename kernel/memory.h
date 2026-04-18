#ifndef MEMORY_H
#define MEMORY_H

// Définitions des adresses et tailles de la mémoire gérée
#define MEM_START_ADDRESS 0x100000    // 1MB
#define MEM_END_ADDRESS   0x1000000   // 16MB
#define PAGE_SIZE         0x1000      // 4KB

// Fonctions de gestion de la mémoire physique
void mem_init(void);
void* mem_alloc(void);
void mem_free(void* ptr);
unsigned int mem_used_kb(void);
unsigned int mem_total_kb(void);

#endif