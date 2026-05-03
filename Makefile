AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
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

$(BUILD)/boot.bin: $(SRC_DIR)/boot/boot.asm | $(BUILD)
	$(AS) $(BFLAGS) $< -o $@

$(BUILD)/kernel_entry.o: $(SRC_DIR)/kernel/kernel_entry.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/isr.o: $(SRC_DIR)/kernel/isr.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/irq.o: $(SRC_DIR)/kernel/irq.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

SRCS_C = \
	kernel/idt.c \
	kernel/irq.c \
	kernel/irq_handler.c \
	kernel/timer.c \
	kernel/memory.c \
	kernel/fault_handler.c \
	kernel/paging.c \
	kernel/screen.c \
	kernel/keyboard.c \
	kernel/terminal.c \
	kernel/mouse.c \
	kernel/kmain.c

OBJS = \
	$(BUILD)/kernel_entry.o \
	$(BUILD)/isr.o \
	$(BUILD)/irq.o \
	$(BUILD)/idt.o \
	$(BUILD)/irq_handler.o \
	$(BUILD)/timer.o \
	$(BUILD)/memory.o \
	$(BUILD)/fault_handler.o \
	$(BUILD)/paging.o \
	$(BUILD)/screen.o \
	$(BUILD)/keyboard.o \
	$(BUILD)/terminal.o \
	$(BUILD)/mouse.o \
	$(BUILD)/kmain.o

$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.bin: $(BUILD)/kernel_entry.o $(OBJS) | $(BUILD)
	$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin
	dd if=/dev/zero of=$@ bs=512 count=2880
	dd if=$(BUILD)/boot.bin of=$@ conv=notrunc
	dd if=$(BUILD)/kernel.bin of=$@ seek=1 conv=notrunc

clean:
	rm -rf $(BUILD) os.img