unsigned int _stack_top;

void kernel_main() {
    _stack_top = 0x100000;
    screen_init();
    screen_write("Kernel started successfully!",30);
    while(1);
}

void _start() {
    asm volatile("movl %0, %%esp" : : "r"(_stack_top));
    kernel_main();
}