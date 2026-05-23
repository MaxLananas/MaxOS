AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I..
LFLAGS = -m elf_i386 -T ../linker.ld --oformat binary
EFLAGS = -f elf
BUILD  = ../build
SRC_DIR = .

VPATH = $(SRC_DIR)

.PHONY: all clean

all: kernel.bin

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/%.o: %.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@

kernel.bin: $(patsubst %.c,%.o,$(wildcard *.c)) | $(BUILD)
	$(LD) $(LFLAGS) $^ -o $@

clean:
	rm -rf $(BUILD) kernel.bin