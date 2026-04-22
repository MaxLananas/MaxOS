AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf
BUILD  = build

.PHONY: all clean

all: os.img

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/boot.bin: boot/boot.asm | $(BUILD)
	$(AS) $(BFLAGS) $< -o $@

$(BUILD)/kernel_entry.o: kernel/kernel_entry.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/isr.o: kernel/isr.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/idt.o: kernel/idt.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/isr_c.o: kernel/isr.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/timer.o: kernel/timer.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/memory.o: kernel/memory.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/fault_handler.o: kernel/fault_handler.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kmain.o: kernel/kmain.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/screen.o: drivers/screen.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/keyboard.o: drivers/keyboard.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/terminal.o: apps/terminal.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

OBJS = \
	$(BUILD)/kernel_entry.o \
	$(BUILD)/isr.o \
	$(BUILD)/idt.o \
	$(BUILD)/isr_c.o \
	$(BUILD)/timer.o \
	$(BUILD)/memory.o \
	$(BUILD)/fault_handler.o \
	$(BUILD)/kmain.o \
	$(BUILD)/screen.o \
	$(BUILD)/keyboard.o \
	$(BUILD)/terminal.o

$(BUILD)/kernel.bin: $(OBJS) | $(BUILD)
	$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin
	dd if=/dev/zero    of=$@ bs=512 count=2880
	dd if=$(BUILD)/boot.bin   of=$@ conv=notrunc
	dd if=$(BUILD)/kernel.bin of=$@ seek=1 conv=notrunc

clean:
	rm -rf $(BUILD) os.img
