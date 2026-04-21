CC = gcc
NASM = nasm
LD = ld
DD = dd

CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
NASMFLAGS = -f bin
LDFLAGS = -m elf_i386 -T linker.ld --oformat binary

OBJS = kernel/start.o kernel/screen.o kernel/exceptions.o kernel/fault_handler.o

all: os.img

boot.bin: boot/boot.asm
	$(NASM) $(NASMFLAGS) $< -o $@

kernel.bin: $(OBJS)
	$(LD) $(LDFLAGS) $^ -o $@

os.img: boot.bin kernel.bin
	$(DD) if=boot.bin of=os.img bs=512
	$(DD) if=kernel.bin of=os.img bs=512 seek=1

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.asm
	$(NASM) -f elf $< -o $@

clean:
	rm -f *.bin *.img *.o

.PHONY: all clean