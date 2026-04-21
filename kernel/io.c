unsigned char inb(unsigned short port) {
    unsigned char ret;
    asm volatile("inb %1, %0" : "=a"(ret) : "dN"(port));
    return ret;
}

void outb(unsigned short port, unsigned char data) {
    asm volatile("outb %0, %1" : : "a"(data), "dN"(port));
}