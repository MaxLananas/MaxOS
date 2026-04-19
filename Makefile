CC = gcc
NASM = nasm
LD = ld
DD = dd

CFLAGS = -m32 -ffreestanding -fno-builtin -fno-pic -fno-pie -nostdlib -nostdinc -Iinclude
NASMFLAGS = -f elf
LDFLAGS = -m elf_i386 -T linker.ld --oformat binary

OBJS = kernel/main.o kernel/isr.o kernel/idt.o kernel/io.o kernel/timer.o \
       kernel/memory.o kernel/syscall.o kernel/fault_handler.o \
       kernel/kernel_entry.o kernel/mce.o drivers/pci.o drivers/keyboard.o \
       drivers/screen.o ui/ui.o ui/window.o ui/widget.o apps/terminal.o

all: os.img

boot.bin: boot/boot.asm
	$(NASM) $(NASMFLAGS) $< -o $@

kernel.bin: $(OBJS)
	$(LD) $(LDFLAGS) $^ -o $@

kernel/%.o: kernel/%.c
	$(CC) $(CFLAGS) -c $< -o $@

kernel/%.o: kernel/%.asm
	$(NASM) $(NASMFLAGS) $< -o $@

drivers/%.o: drivers/%.c
	$(CC) $(CFLAGS) -c $< -o $@

ui/%.o: ui/%.c
	$(CC) $(CFLAGS) -c $< -o $@

apps/%.o: apps/%.c
	$(CC) $(CFLAGS) -c $< -o $@

os.img: boot.bin kernel.bin
	$(DD) if=/dev/zero of=$@ bs=512 count=2880
	$(DD) if=boot.bin of=$@ conv=notrunc
	$(DD) if=kernel.bin of=$@ seek=1 conv=notrunc

clean:
	rm -f *.bin *.o os.img