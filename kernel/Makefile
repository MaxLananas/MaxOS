AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T ../linker.ld --oformat binary
EFLAGS = -f elf

.PHONY: all clean

all: kernel.bin

kernel.bin: kernel_entry.o isr.o idt_load.o irq.o idt.o isr.o timer.o fault_handler.o keyboard.o screen.o terminal.o kmain.o
	$(LD) $(LFLAGS) $^ -o $@

%.o: %.asm
	$(AS) $(EFLAGS) $< -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf *.o kernel.bin