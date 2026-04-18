#ifndef IDT_H
#define IDT_H

/* Définitions des ports PIC */
#define PIC1_COMMAND    0x20
#define PIC1_DATA       0x21
#define PIC2_COMMAND    0xA0
#define PIC2_DATA       0xA1

/* Définitions des ICW (Initialisation Control Words) */
#define ICW1_INIT       0x10    /* Initialisation */
#define ICW1_IC4        0x01    /* ICW4 est nécessaire */
#define ICW4_8086       0x01    /* Mode 8086/88 */

/* Définition de l'EOI (End-Of-Interrupt) */
#define PIC_EOI         0x20

/* Structure d'une entrée IDT */
struct idt_entry {
    unsigned short base_low;    /* Les 16 bits de poids faible de l'adresse du gestionnaire */
    unsigned short selector;    /* Sélecteur de segment du gestionnaire */
    unsigned char  zero;        /* Toujours zéro */
    unsigned char  flags;       /* Type de gate, DPL, P */
    unsigned short base_high;   /* Les 16 bits de poids fort de l'adresse du gestionnaire */
} __attribute__((packed));      /* Empêche le compilateur d'ajouter du padding */

/* Structure du pointeur IDT pour la commande LIDT */
struct idt_ptr {
    unsigned short limit;       /* Taille de l'IDT - 1 */
    unsigned int   base;        /* Adresse de base de l'IDT */
} __attribute__((packed));

/* Déclarations des fonctions */
void idt_init(void);
void pic_remap(void);
void pic_mask_irq(unsigned char irq_line);
void pic_unmask_irq(unsigned char irq_line);
void pic_send_eoi(unsigned char irq_line);

#endif