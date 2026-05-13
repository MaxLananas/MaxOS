void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);
    for (;;);
}