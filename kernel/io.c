unsigned char inb(unsigned short port) {
    unsigned char ret;
    asm volatile("inb %1, %0" : "=a"(ret) : "d"(port));
    return ret;
}

void outb(unsigned short port, unsigned char data) {
    asm volatile("outb %1, %0" : : "d"(port), "a"(data));
}