AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T ../linker.ld --oformat binary
EFLAGS = -f elf

VPATH = ../drivers

.PHONY: all clean

all: ../os.img

../os.img: ../build/boot.bin ../build/kernel.bin
	dd if=/dev/zero of=$@ bs=512 count=2880
	dd if=../build/boot.bin of=$@ conv=notrunc
	dd if=../build/kernel.bin of=$@ seek=1 conv=notrunc

../build/boot.bin: boot.asm | ../build
	$(AS) $(EFLAGS) $< -o $@

../build/kernel_entry.o: kernel_entry.asm | ../build
	$(AS) $(EFLAGS) $< -o $@

../build/isr.o: isr.asm | ../build
	$(AS) $(EFLAGS) $< -o $@

../build/idt_load.o: idt_load.asm | ../build
	$(AS) $(EFLAGS) $< -o $@

../build/ap_start.o: ap_start.asm | ../build
	$(AS) $(EFLAGS) $< -o $@

../build/%.o: %.c | ../build
	$(CC) $(CFLAGS) -c $< -o $@

../build/kernel.bin: ../build/kernel_entry.o ../build/isr.o ../build/idt_load.o ../build/ap_start.o $(patsubst %.c,../build/%.o,$(wildcard *.c) drivers/*.c)
	$(LD) $(LFLAGS) $^ -o $@

../build:
	mkdir -p ../build

clean:
	rm -rf ../build ../os.img