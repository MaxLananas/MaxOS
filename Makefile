CC = gcc
NASM = nasm
LD = ld
DD = dd

CFLAGS = -m32 -ffreestanding -fno-builtin -fno-pic -fno-pie -nostdlib -nostdinc -Iinclude
NASMFLAGS = -f elf
LDFLAGS = -m elf_i386 -T linker.ld --oformat binary

OBJS = kernel/main.o kernel/isr.o kernel/idt.o kernel/io.o kernel/timer.o \
       kernel/memory.o kernel/pmm.o kernel/syscall.o kernel/fault_handler.o \
       kernel/kernel_entry.o kernel/mce.o kernel/exceptions.o \
       kernel/screen.o kernel/paging.o \
       drivers/pci.o drivers/keyboard.o \
       drivers/screen.o ui/ui.o ui/window.o ui/widget.o apps/terminal.o

all: os.img

boot.bin: boot/boot.asm
	$(NASM) $(NASMFLAGS) $< -o $@

kernel.bin: $(OBJS)
	$(LD) $(LDFLAGS) $^ -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.asm
	$(NASM) $(NASMFLAGS) $< -o $@

os.img: boot.bin kernel.bin
	$(DD) if=/dev/zero of=os.img bs=512 count=2880
	$(DD) if=boot.bin of=os.img conv=notrunc
	$(DD) if=kernel.bin of=os.img seek=1 conv=notrunc

clean:
	rm -f *.bin *.img
	rm -f kernel/*.o drivers/*.o ui/*.o apps/*.o