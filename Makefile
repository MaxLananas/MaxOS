CC = gcc
NASM = nasm
LD = ld
DD = dd

CFLAGS = -m32 -ffreestanding -fno-builtin -fno-pic -fno-pie -nostdlib -nostdinc -Iinclude
NASMFLAGS = -f elf
LDFLAGS = -m elf_i386 -T linker.ld --oformat binary

OBJS = kernel/main.o kernel/isr.o kernel/idt.o kernel/io.o kernel/timer.o kernel/memory.o kernel/syscall.o kernel/fault_handler.o kernel/kernel_entry.o drivers/pci.o drivers/keyboard.o drivers/screen.o

all: os.img

boot.bin: boot/boot.asm
	$(NASM) $(NASMFLAGS) boot/boot.asm -o boot.bin

kernel.bin: $(OBJS)
	$(LD) $(LDFLAGS) $(OBJS) -o kernel.bin

kernel/%.o: kernel/%.c
	$(CC) $(CFLAGS) -c $< -o $@

kernel/%.o: kernel/%.asm
	$(NASM) $(NASMFLAGS) $< -o $@

drivers/%.o: drivers/%.c
	$(CC) $(CFLAGS) -c $< -o $@

drivers/%.o: drivers/%.asm
	$(NASM) $(NASMFLAGS) $< -o $@

os.img: boot.bin kernel.bin
	$(DD) if=boot.bin of=os.img bs=512 count=1
	$(DD) if=kernel.bin of=os.img bs=512 seek=1

clean:
	rm -f *.bin *.o os.img