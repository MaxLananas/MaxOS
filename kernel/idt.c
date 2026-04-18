#include "idt.h"
#include "../drivers/screen.h"

/* Définition de la table des descripteurs d'interruptions */
static struct idt_entry idt_entries[256];
static struct idt_ptr   idt_pointer;

/* Déclarations externes des gestionnaires d'interruptions en ASM */
extern void isr0(void);
extern void isr1(void);
extern void isr2(void);
extern void isr3(void);
extern void isr4(void);
extern void isr5(void);
extern void isr6(void);
extern void isr7(void);
extern void isr8(void);
extern void isr9(void);
extern void isr10(void);
extern void isr11(void);
extern void isr12(void);
extern void isr13(void);
extern void isr14(void);
extern void isr15(void);
extern void isr16(void);
extern void isr17(void);
extern void isr18(void);
extern void isr19(void);
extern void isr20(void);
extern void isr21(void);
extern void isr22(void);
extern void isr23(void);
extern void isr24(void);
extern void isr25(void);
extern void isr26(void);
extern void isr27(void);
extern void isr28(void);
extern void isr29(void);
extern void isr30(void);
extern void isr31(void);

/* Déclarations externes des gestionnaires d'IRQ en ASM */
extern void irq0(void);
extern void irq1(void);
extern void irq2(void);
extern void irq3(void);
extern void irq4(void);
extern void irq5(void);
extern void irq6(void);
extern void irq7(void);
extern void irq8(void);
extern void irq9(void);
extern void irq10(void);
extern void irq11(void);
extern void irq12(void);
extern void irq13(void);
extern void irq14(void);
extern void irq15(void);

/*
 * Fonction pour écrire un octet sur un port I/O.
 */
static void outb(unsigned short port, unsigned char value) {
    __asm__ volatile("outb %0, %1" : : "a"(value), "Nd"(port));
}

/*
 * Fonction pour lire un octet depuis un port I/O.
 */
static unsigned char inb(unsigned short port) {
    unsigned char ret;
    __asm__ volatile("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

/*
 * Fonction pour définir une entrée dans l'IDT.
 * base: adresse du gestionnaire d'interruption
 * selector: sélecteur de segment (0x08 pour le segment de code du kernel)
 * flags: drapeaux de l'entrée (type de gate, DPL, P)
 */
static void idt_set_gate(unsigned char num, unsigned int base, unsigned short selector, unsigned char flags) {
    idt_entries[num].base_low = (unsigned short)(base & 0xFFFF);
    idt_entries[num].base_high = (unsigned short)((base >> 16) & 0xFFFF);
    idt_entries[num].selector = selector;
    idt_entries[num].zero = 0;
    idt_entries[num].flags = flags;
}

/*
 * Initialise le contrôleur d'interruption programmable (PIC) 8259.
 * Remappe les IRQ pour éviter les conflits avec les exceptions x86.
 * IRQ0-7 -> INT 32-39
 * IRQ8-15 -> INT 40-47
 */
void pic_remap(void) {
    /* Initialisation Control Word 1 (ICW1) */
    outb(PIC1_COMMAND, ICW1_INIT | ICW1_IC4); /* Initialise PIC maître, attend ICW4 */
    outb(PIC2_COMMAND, ICW1_INIT | ICW1_IC4); /* Initialise PIC esclave, attend ICW4 */

    /* Initialisation Control Word 2 (ICW2) */
    outb(PIC1_DATA, 0x20); /* Offset du PIC maître (IRQ0-7 -> INT 32-39) */
    outb(PIC2_DATA, 0x28); /* Offset du PIC esclave (IRQ8-15 -> INT 40-47) */

    /* Initialisation Control Word 3 (ICW3) */
    outb(PIC1_DATA, 0x04); /* PIC maître a un esclave sur IRQ2 (0000 0100) */
    outb(PIC2_DATA, 0x02); /* PIC esclave est connecté à l'IRQ2 du maître (0000 0010) */

    /* Initialisation Control Word 4 (ICW4) */
    outb(PIC1_DATA, ICW4_8086); /* Mode 8086/88 pour PIC maître */
    outb(PIC2_DATA, ICW4_8086); /* Mode 8086/88 pour PIC esclave */

    /* Masquer toutes les IRQ par défaut */
    outb(PIC1_DATA, 0xFF);
    outb(PIC2_DATA, 0xFF);
}

/*
 * Masque une IRQ spécifique.
 */
void pic_mask_irq(unsigned char irq_line) {
    unsigned short port;
    unsigned char value;

    if (irq_line < 8) {
        port = PIC1_DATA;
    } else {
        port = PIC2_DATA;
        irq_line -= 8;
    }
    value = inb(port) | (1 << irq_line);
    outb(port, value);
}

/*
 * Démasque une IRQ spécifique.
 */
void pic_unmask_irq(unsigned char irq_line) {
    unsigned short port;
    unsigned char value;

    if (irq_line < 8) {
        port = PIC1_DATA;
    } else {
        port = PIC2_DATA;
        irq_line -= 8;
    }
    value = inb(port) & ~(1 << irq_line);
    outb(port, value);
}

/*
 * Envoie un End-Of-Interrupt (EOI) au PIC.
 * Doit être appelé à la fin de chaque gestionnaire d'IRQ.
 */
void pic_send_eoi(unsigned char irq_line) {
    if (irq_line >= 8) {
        outb(PIC2_COMMAND, PIC_EOI); /* EOI pour le PIC esclave */
    }
    outb(PIC1_COMMAND, PIC_EOI); /* EOI pour le PIC maître */
}

/*
 * Structure pour stocker l'état des registres lors d'une interruption.
 * Poussé sur la pile par les stubs ASM.
 */
struct registers {
    unsigned int edi, esi, ebp, esp_dummy, ebx, edx, ecx, eax; /* Pushed by pusha */
    unsigned int int_no, err_code; /* Pushed by our custom ISR stub */
    unsigned int eip, cs, eflags, useresp, ss; /* Pushed by the CPU */
};

/*
 * Gestionnaire C générique pour toutes les exceptions.
 * Affiche un écran de panique et les informations de l'exception.
 */
void exception_handler(struct registers regs) {
    const char* exception_messages[] = {
        "Division By Zero",
        "Debug",
        "Non-Maskable Interrupt",
        "Breakpoint",
        "Overflow",
        "Bound Range Exceeded",
        "Invalid Opcode",
        "Device Not Available",
        "Double Fault",
        "Coprocessor Segment Overrun",
        "Invalid TSS",
        "Segment Not Present",
        "Stack-Segment Fault",
        "General Protection Fault",
        "Page Fault",
        "Reserved",
        "x87 Floating-Point Exception",
        "Alignment Check",
        "Machine Check",
        "SIMD Floating-Point Exception",
        "Virtualization Exception",
        "Control Protection Exception",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved"
    };

    /* Écran de panique rouge */
    v_fill(0, 0, VGA_H, VGA_W, C_WHITE, C_RED);
    v_str(2, 2, "!!! MAXOS KERNEL PANIC !!!", C_WHITE, C_RED);
    v_str(4, 2, "Une exception fatale est survenue.", C_WHITE, C_RED);
    v_str(6, 2, "Exception:", C_WHITE, C_RED);
    v_str(6, 13, exception_messages[regs.int_no], C_WHITE, C_RED);
    v_str(6, 45, " (#", C_WHITE, C_RED);
    v_int(6, 48, regs.int_no, C_WHITE, C_RED);
    v_str(6, 50, ")", C_WHITE, C_RED);

    if (regs.err_code != 0) {
        v_str(7, 2, "Error Code:", C_WHITE, C_RED);
        v_int(7, 14, regs.err_code, C_WHITE, C_RED);
    }

    v_str(9, 2, "Registers state:", C_WHITE, C_RED);
    v_str(10, 2, "EAX:", C_WHITE, C_RED); v_int2(10, 7, regs.eax, C_WHITE, C_RED);
    v_str(11, 2, "EBX:", C_WHITE, C_RED); v_int2(11, 7, regs.ebx, C_WHITE, C_RED);
    v_str(12, 2, "ECX:", C_WHITE, C_RED); v_int2(12, 7, regs.ecx, C_WHITE, C_RED);
    v_str(13, 2, "EDX:", C_WHITE, C_RED); v_int2(13, 7, regs.edx, C_WHITE, C_RED);
    v_str(10, 20, "ESI:", C_WHITE, C_RED); v_int2(10, 25, regs.esi, C_WHITE, C_RED);
    v_str(11, 20, "EDI:", C_WHITE, C_RED); v_int2(11, 25, regs.edi, C_WHITE, C_RED);
    v_str(12, 20, "EBP:", C_WHITE, C_RED); v_int2(12, 25, regs.ebp, C_WHITE, C_RED);
    v_str(13, 20, "ESP:", C_WHITE, C_RED); v_int2(13, 25, regs.useresp, C_WHITE, C_RED); /* useresp est le ESP avant l'interruption */

    v_str(15, 2, "EIP:", C_WHITE, C_RED); v_int2(15, 7, regs.eip, C_WHITE, C_RED);
    v_str(16, 2, "CS:", C_WHITE, C_RED);  v_int2(16, 7, regs.cs, C_WHITE, C_RED);
    v_str(17, 2, "EFLAGS:", C_WHITE, C_RED); v_int2(17, 10, regs.eflags, C_WHITE, C_RED);

    v_str(20, 2, "Le systeme a ete arrete.", C_WHITE, C_RED);

    /* Désactiver les interruptions et arrêter le CPU */
    __asm__ volatile("cli");
    for (;;) {
        __asm__ volatile("hlt");
    }
}

/*
 * Initialise l'IDT et le PIC.
 */
void idt_init(void) {
    /* Initialise le pointeur IDT */
    idt_pointer.limit = (sizeof(struct idt_entry) * 256) - 1;
    idt_pointer.base = (unsigned int)&idt_entries;

    /* Met à zéro toute l'IDT */
    unsigned int i;
    for (i = 0; i < 256; i++) {
        idt_entries[i].base_low = 0;
        idt_entries[i].base_high = 0;
        idt_entries[i].selector = 0;
        idt_entries[i].zero = 0;
        idt_entries[i].flags = 0;
    }

    /* Définit les gestionnaires d'exceptions (0-31) */
    idt_set_gate(0, (unsigned int)isr0, 0x08, 0x8E);
    idt_set_gate(1, (unsigned int)isr1, 0x08, 0x8E);
    idt_set_gate(2, (unsigned int)isr2, 0x08, 0x8E);
    idt_set_gate(3, (unsigned int)isr3, 0x08, 0x8E);
    idt_set_gate(4, (unsigned int)isr4, 0x08, 0x8E);
    idt_set_gate(5, (unsigned int)isr5, 0x08, 0x8E);
    idt_set_gate(6, (unsigned int)isr6, 0x08, 0x8E);
    idt_set_gate(7, (unsigned int)isr7, 0x08, 0x8E);
    idt_set_gate(8, (unsigned int)isr8, 0x08, 0x8E);
    idt_set_gate(9, (unsigned int)isr9, 0x08, 0x8E);
    idt_set_gate(10, (unsigned int)isr10, 0x08, 0x8E);
    idt_set_gate(11, (unsigned int)isr11, 0x08, 0x8E);
    idt_set_gate(12, (unsigned int)isr12, 0x08, 0x8E);
    idt_set_gate(13, (unsigned int)isr13, 0x08, 0x8E);
    idt_set_gate(14, (unsigned int)isr14, 0x08, 0x8E);
    idt_set_gate(15, (unsigned int)isr15, 0x08, 0x8E);
    idt_set_gate(16, (unsigned int)isr16, 0x08, 0x8E);
    idt_set_gate(17, (unsigned int)isr17, 0x08, 0x8E);
    idt_set_gate(18, (unsigned int)isr18, 0x08, 0x8E);
    idt_set_gate(19, (unsigned int)isr19, 0x08, 0x8E);
    idt_set_gate(20, (unsigned int)isr20, 0x08, 0x8E);
    idt_set_gate(21, (unsigned int)isr21, 0x08, 0x8E);
    idt_set_gate(22, (unsigned int)isr22, 0x08, 0x8E);
    idt_set_gate(23, (unsigned int)isr23, 0x08, 0x8E);
    idt_set_gate(24, (unsigned int)isr24, 0x08, 0x8E);
    idt_set_gate(25, (unsigned int)isr25, 0x08, 0x8E);
    idt_set_gate(26, (unsigned int)isr26, 0x08, 0x8E);
    idt_set_gate(27, (unsigned int)isr27, 0x08, 0x8E);
    idt_set_gate(28, (unsigned int)isr28, 0x08, 0x8E);
    idt_set_gate(29, (unsigned int)isr29, 0x08, 0x8E);
    idt_set_gate(30, (unsigned int)isr30, 0x08, 0x8E);
    idt_set_gate(31, (unsigned int)isr31, 0x08, 0x8E);

    /* Remappe le PIC et définit les gestionnaires d'IRQ (32-47) */
    pic_remap();
    idt_set_gate(32, (unsigned int)irq0, 0x08, 0x8E); /* Timer */
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E); /* Clavier */
    idt_set_gate(34, (unsigned int)irq2, 0x08, 0x8E);
    idt_set_gate(35, (unsigned int)irq3, 0x08, 0x8E);
    idt_set_gate(36, (unsigned int)irq4, 0x08, 0x8E);
    idt_set_gate(37, (unsigned int)irq5, 0x08, 0x8E);
    idt_set_gate(38, (unsigned int)irq6, 0x08, 0x8E);
    idt_set_gate(39, (unsigned int)irq7, 0x08, 0x8E);
    idt_set_gate(40, (unsigned int)irq8, 0x08, 0x8E);
    idt_set_gate(41, (unsigned int)irq9, 0x08, 0x8E);
    idt_set_gate(42, (unsigned int)irq10, 0x08, 0x8E);
    idt_set_gate(43, (unsigned int)irq11, 0x08, 0x8E);
    idt_set_gate(44, (unsigned int)irq12, 0x08, 0x8E);
    idt_set_gate(45, (unsigned int)irq13, 0x08, 0x8E);
    idt_set_gate(46, (unsigned int)irq14, 0x08, 0x8E);
    idt_set_gate(47, (unsigned int)irq15, 0x08, 0x8E);

    /* Charge l'IDT */
    __asm__ volatile("lidt %0" : : "m"(idt_pointer));

    /* Active les interruptions */
    __asm__ volatile("sti");
}