AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I..
LFLAGS = -m elf_i386 -T ../linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf
BUILD  = ../build
SRC_DIR = ..

VPATH = $(SRC_DIR)/kernel

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
	idt.c \
	isr.c \
	irq.c \
	irq_handler.c \
	timer.c \
	memory.c \
	fault_handler.c \
	page_fault.c \
	paging.c \
	pmm.c \
	vmm.c \
	heap.c \
	screen.c \
	keyboard.c \
	terminal.c \
	mouse.c \
	kmain.c

OBJS = \
	$(BUILD)/kernel_entry.o \
	$(BUILD)/isr.o \
	$(BUILD)/irq.o \
	$(BUILD)/idt.o \
	$(BUILD)/irq_handler.o \
	$(BUILD)/timer.o \
	$(BUILD)/memory.o \
	$(BUILD)/fault_handler.o \
	$(BUILD)/page_fault.o \
	$(BUILD)/paging.o \
	$(BUILD)/pmm.o \
	$(BUILD)/vmm.o \
	$(BUILD)/heap.o \
	$(BUILD)/screen.o \
	$(BUILD)/keyboard.o \
	$(BUILD)/terminal.o \
	$(BUILD)/mouse.o \
	$(BUILD)/kmain.o

$(BUILD)/idt.o: idt.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/irq.o: irq.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/irq_handler.o: irq_handler.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/timer.o: timer.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/memory.o: memory.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/fault_handler.o: fault_handler.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/page_fault.o: page_fault.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/paging.o: paging.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/pmm.o: pmm.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/vmm.o: vmm.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/heap.o: heap.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/screen.o: screen.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/keyboard.o: keyboard.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/terminal.o: terminal.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/mouse.o: mouse.c | $(BUILD)
	$(CC)