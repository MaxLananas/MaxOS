#ifndef IO_H
#define IO_H

static inline void outb(unsigned short p, unsigned char v) {
    asm volatile("outb %0,%1"::"a"(v),"Nd"(p));
}

static inline unsigned char inb(unsigned short p) {
    unsigned char v;
    asm volatile("inb %1,%0":"=a"(v):"Nd"(p));
    return v;
}

#endif