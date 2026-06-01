AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf
BUILD  = build
SRC_DIR = .

.PHONY: all clean

all: os.img

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/boot.bin: $(SRC_DIR)/boot.asm | $(BUILD)
	$(AS) $(BFLAGS) $< -o $@

$(BUILD)/kernel_entry.o: $(SRC_DIR)/kernel_entry.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/isr.o: $(SRC_DIR)/isr.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/irq.o: $(SRC_DIR)/irq.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/idt_load.o: $(SRC_DIR)/idt_load.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

SRCS_C = \
	idt.c \
	timer.c \
	keyboard.c \
	screen.c \
	mouse.c \
	irq.c \
	exceptions.c \
	fault_handler.c \
	mem.c \
	paging.c \
	heap.c \
	ata.c \
	terminal.c \
	devfs.c \
	vfs.c \
	kmain.c \
	vmm.c \
	vmm_shadow.c \
	vmm_ept.c \
	mmu.c \
	pmm.c \
	acpi.c \
	acpi_tables.c \
	acpi_fadt.c \
	acpi_madt.c \
	acpi_hpet.c

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