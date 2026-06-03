AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -Ikernel
LFLAGS = -m elf_i386 -T linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf
BUILD  = build
SRC_DIR = .

VPATH = kernel drivers

.PHONY: all clean

all: os.img

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/boot.bin: $(SRC_DIR)/boot.asm | $(BUILD)
	$(AS) $(BFLAGS) $< -o $@

$(BUILD)/kernel_entry.o: $(SRC_DIR)/kernel/kernel_entry.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/isr.o: $(SRC_DIR)/kernel/isr.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/irq.o: $(SRC_DIR)/kernel/irq.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/idt_load.o: $(SRC_DIR)/kernel/idt_load.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

SRCS_C = \
	kernel/idt.c \
	kernel/timer.c \
	kernel/keyboard.c \
	kernel/screen.c \
	kernel/mouse.c \
	kernel/irq.c \
	kernel/exceptions.c \
	kernel/fault_handler.c \
	kernel/mem.c \
	kernel/paging.c \
	kernel/heap.c \
	kernel/ata.c \
	kernel/terminal.c \
	kernel/devfs.c \
	kernel/vfs.c \
	kernel/kmain.c

OBJS = \
	$(BUILD)/kernel_entry.o \
	$(BUILD)/isr.o \
	$(BUILD)/irq.o \
	$(BUILD)/idt_load.o \
	$(patsubst %.c,$(BUILD)/%.o,$(SRCS_C))

$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.bin: $(OBJS) | $(BUILD)
	$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin
	dd if=/dev/zero of=$@ bs=512 count=2880
	dd if=$(BUILD)/boot.bin of=$@ conv=notrunc
	dd if=$(BUILD)/kernel.bin of=$@ seek=1 conv=notrunc

clean:
	rm -rf $(BUILD) os.img