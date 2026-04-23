#ifndef IO_H
#define IO_H

static inline void outb(unsigned short port, unsigned char val) {
    __asm__ volatile("outb %0, %1" :: "a"(val), "Nd"(port));
}

static inline unsigned char inb(unsigned short port) {
    unsigned char val;
    __asm__ volatile("inb %1, %0" : "=a"(val) : "Nd"(port));
    return val;
}

static inline void outw(unsigned short port, unsigned short val) {
    __asm__ volatile("outw %0, %1" :: "a"(val), "Nd"(port));
}

static inline unsigned short inw(unsigned short port) {
    unsigned short val;
    __asm__ volatile("inw %1, %0" : "=a"(val) : "Nd"(port));
    return val;
}

static inline void outl(unsigned short port, unsigned int val) {
    __asm__ volatile("outl %0, %1" :: "a"(val), "Nd"(port));
}

static inline unsigned int inl(unsigned short port) {
    unsigned int val;
    __asm__ volatile("inl %1, %0" : "=a"(val) : "Nd"(port));
    return val;
}

static inline void io_wait(void) {
    outb(0x80, 0x00);
}

#endif