AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf
BUILD  = build
SRC_DIR = .

VPATH = $(SRC_DIR)/kernel:$(SRC_DIR)/drivers:$(SRC_DIR)/apps

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

SRCS_C = \
	$(SRC_DIR)/kernel/idt.c \
	$(SRC_DIR)/kernel/isr.c \
	$(SRC_DIR)/kernel/timer.c \
	$(SRC_DIR)/kernel/memory.c \
	$(SRC_DIR)/kernel/fault_handler.c \
	$(SRC_DIR)/kernel/page_fault.c \
	$(SRC_DIR)/kernel/paging.c \
	$(SRC_DIR)/kernel/pmm.c \
	$(SRC_DIR)/kernel/kmain.c \
	$(SRC_DIR)/drivers/screen.c \
	$(SRC_DIR)/drivers/keyboard.c \
	$(SRC_DIR)/apps/terminal.c

OBJS = \
	$(BUILD)/kernel_entry.o \
	$(BUILD)/isr.o \
	$(BUILD)/idt.o \
	$(BUILD)/isr_c.o \
	$(BUILD)/timer.o \
	$(BUILD)/memory.o \
	$(BUILD)/fault_handler.o \
	$(BUILD)/page_fault.o \
	$(BUILD)/paging.o \
	$(BUILD)/pmm.o \
	$(BUILD)/kmain.o \
	$(BUILD)/screen.o \
	$(BUILD)/keyboard.o \
	$(BUILD)/terminal.o

$(BUILD)/idt.o: $(SRC_DIR)/kernel/idt.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/isr_c.o: $(SRC_DIR)/kernel/isr.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/timer.o: $(SRC_DIR)/kernel/timer.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/memory.o: $(SRC_DIR)/kernel/memory.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/fault_handler.o: $(SRC_DIR)/kernel/fault_handler.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/page_fault.o: $(SRC_DIR)/kernel/page_fault.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/paging.o: $(SRC_DIR)/kernel/paging.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/pmm.o: $(SRC_DIR)/kernel/pmm.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kmain.o: $(SRC_DIR)/kernel/kmain.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/screen.o: $(SRC_DIR)/drivers/screen.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/keyboard.o: $(SRC_DIR)/drivers/keyboard.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/terminal.o: $(SRC_DIR)/apps/terminal.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.bin: $(BUILD)/kernel_entry.o $(OBJS) | $(BUILD)
	$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin
	dd if=/dev/zero of=$@ bs=512 count=2880
	dd if=$(BUILD)/boot.bin of=$@ conv=notrunc
	dd if=$(BUILD)/kernel.bin of=$@ seek=1 conv=notrunc

clean:
	rm -rf $(BUILD) os.img