AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T ../linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf
BUILD  = ../build
SRC_DIR = .

.PHONY: all clean

all: kernel.bin

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.o: $(SRC_DIR)/%.asm | $(BUILD)
	$(AS) $(EFLAGS) $< -o $@

$(BUILD)/%.o: $(SRC_DIR)/%.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.bin: $(wildcard $(BUILD)/*.o) | $(BUILD)
	$(LD) $(LFLAGS) $^ -o $@

clean:
	rm -rf $(BUILD) kernel.bin