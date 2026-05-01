AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf
BUILD  = build
SRC_DIR = .

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
	kernel/idt.c \
	kernel/isr.c \
	kernel/irq.c \
	kernel/irq_handler.c \
	kernel/timer.c \
	kernel/memory.c \
	kernel/fault_handler.c \
	kernel/page_fault.c \
	kernel/paging.c \
	kernel/pmm.c \
	kernel/vmm.c \
	kernel/heap.c \
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

$(BUILD)/idt.o: kernel/idt.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/irq.o: kernel/irq.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/irq_handler.o: kernel/irq_handler.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/timer.o: kernel/timer.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/memory.o: kernel/memory.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/fault_handler.o: kernel/fault_handler.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/page_fault.o: kernel/page_fault.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/paging.o: kernel/paging.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/pmm.o: kernel/pmm.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/vmm.o: kernel/vmm.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/heap.o: kernel/heap.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/screen.o: kernel/screen.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/keyboard.o: kernel/keyboard.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/terminal.o: kernel/terminal.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/mouse.o: kernel/mouse.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kmain.o: kernel/kmain.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.bin: $(BUILD)/kernel_entry.o $(OBJS) | $(BUILD)
	$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin
	dd if=/dev/zero of=$@ bs=512 count=2880
	dd if=$(BUILD)/boot.bin of=$@ conv=notrunc
	dd if=$(BUILD)/kernel.bin of=$@ seek=1 conv=notrunc

clean:
	rm -rf $(BUILD) os.img