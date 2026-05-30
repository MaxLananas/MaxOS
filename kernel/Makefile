AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I..
LFLAGS = -m elf_i386 -T ../linker.ld --oformat binary
EFLAGS = -f elf

.PHONY: all clean

all: kernel.bin

kernel.bin: kernel_entry.o isr.o irq.o idt_load.o \
            idt.o timer.o keyboard.o screen.o mouse.o \
            irq.o exceptions.o fault_handler.o kmain.o \
            mem.o paging.o heap.o ata.o terminal.o devfs.o vfs.o
	$(LD) $(LFLAGS) $^ -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.asm
	$(AS) $(EFLAGS) $< -o $@

clean:
	rm -f *.o kernel.bin