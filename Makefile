ASM  = nasm
CC   = gcc
LD   = ld
QEMU = qemu-system-i386

CFLAGS = -m32 -ffreestanding -fno-stack-protector -fno-builtin \
         -fno-pic -fno-pie -nostdlib -nostdinc -w -c

LFLAGS = -m elf_i386 -T linker.ld --oformat binary

.PHONY: all clean run

all: prepare build/os.img
	@echo ""
	@echo "  MaxOS compile !"
	@echo "  make run  pour lancer"
	@echo ""

prepare:
	@mkdir -p build

build/boot.bin: boot/boot.asm
	$(ASM) -f bin $< -o $@

build/kernel_entry.o: kernel/kernel_entry.asm
	$(ASM) -f elf $< -o $@

build/kernel.o: kernel/kernel.c
	$(CC) $(CFLAGS) $< -o $@

build/screen.o: drivers/screen.c
	$(CC) $(CFLAGS) $< -o $@

build/keyboard.o: drivers/keyboard.c
	$(CC) $(CFLAGS) $< -o $@

build/ui.o: ui/ui.c
	$(CC) $(CFLAGS) $< -o $@

build/notepad.o: apps/notepad.c
	$(CC) $(CFLAGS) $< -o $@

build/terminal.o: apps/terminal.c
	$(CC) $(CFLAGS) $< -o $@

build/sysinfo.o: apps/sysinfo.c
	$(CC) $(CFLAGS) $< -o $@

build/about.o: apps/about.c
	$(CC) $(CFLAGS) $< -o $@

build/kernel.bin: \
    build/kernel_entry.o \
    build/kernel.o \
    build/screen.o \
    build/keyboard.o \
    build/ui.o \
    build/notepad.o \
    build/terminal.o \
    build/sysinfo.o \
    build/about.o
	$(LD) $(LFLAGS) $^ -o $@

build/os.img: build/boot.bin build/kernel.bin
	cat $^ > $@
	truncate -s 1474560 $@

# QEMU avec -no-fd-bootchk et keyboard layout
run: build/os.img
	$(QEMU) \
	  -drive format=raw,file=build/os.img,if=floppy \
	  -boot a \
	  -vga std \
	  -k fr \
	  -no-fd-bootchk

clean:
	@rm -rf build/
	@echo "Nettoye !"