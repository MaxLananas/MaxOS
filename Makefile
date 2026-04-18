ASM  = nasm
CC   = gcc
LD   = ld
QEMU = qemu-system-i386

BUILD_DIR = build

CFLAGS = -m32 -ffreestanding -fno-stack-protector -fno-builtin \
         -fno-pic -fno-pie -nostdlib -nostdinc -w -c

LFLAGS = -m elf_i386 -T linker.ld --oformat binary

.PHONY: all clean run run-nographic

# ======================
# Build principal
# ======================

all: prepare $(BUILD_DIR)/os.img
	@echo ""
	@echo "  MaxOS compilé !"
	@echo "  make run pour lancer"
	@echo ""

prepare:
	@mkdir -p $(BUILD_DIR)

# ======================
# Compilation
# ======================

$(BUILD_DIR)/boot.bin: boot/boot.asm
	$(ASM) -f bin $< -o $@

$(BUILD_DIR)/kernel_entry.o: kernel/kernel_entry.asm
	$(ASM) -f elf $< -o $@

$(BUILD_DIR)/kernel.o: kernel/kernel.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/screen.o: drivers/screen.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/keyboard.o: drivers/keyboard.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/ui.o: ui/ui.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/notepad.o: apps/notepad.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/terminal.o: apps/terminal.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/sysinfo.o: apps/sysinfo.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/about.o: apps/about.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/kernel.bin: \
    $(BUILD_DIR)/kernel_entry.o \
    $(BUILD_DIR)/kernel.o \
    $(BUILD_DIR)/screen.o \
    $(BUILD_DIR)/keyboard.o \
    $(BUILD_DIR)/ui.o \
    $(BUILD_DIR)/notepad.o \
    $(BUILD_DIR)/terminal.o \
    $(BUILD_DIR)/sysinfo.o \
    $(BUILD_DIR)/about.o
	$(LD) $(LFLAGS) $^ -o $@

$(BUILD_DIR)/os.img: $(BUILD_DIR)/boot.bin $(BUILD_DIR)/kernel.bin
	@echo "Construction de l'image disque..."
	@cat $^ > $@
	@truncate -s 1474560 $@
	@echo "Image disque créée : $(BUILD_DIR)/os.img"

# ======================
# QEMU
# ======================

run: $(BUILD_DIR)/os.img
	$(QEMU) \
		-drive format=raw,file=$(BUILD_DIR)/os.img,if=floppy \
		-boot a \
		-vga std \
		-k fr \
		-m 32 \
		-no-fd-bootchk \
		-no-reboot

run-nographic: $(BUILD_DIR)/os.img
	$(QEMU) \
		-drive format=raw,file=$(BUILD_DIR)/os.img,if=floppy \
		-boot a \
		-nographic \
		-no-reboot

# ======================
# Clean
# ======================

clean:
	@rm -rf $(BUILD_DIR)
	@echo "Nettoyage terminé !"
