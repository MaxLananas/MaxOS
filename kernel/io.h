#ifndef IO_H
#define IO_H

static inline void outb(unsigned short port, unsigned char val) {
    asm volatile("outb %0,%1"::"a"(val),"Nd"(port));
}

static inline unsigned char inb(unsigned short port) {
    unsigned char v;
    asm volatile("inb %1,%0":"=a"(v):"Nd"(port));
    return v;
}

#endif