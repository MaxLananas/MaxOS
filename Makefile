ASM  = nasm
CC   = gcc
LD   = ld
QEMU = qemu-system-i386

BUILD_DIR = build

CFLAGS = -m32 -ffreestanding -fno-stack-protector -fno-builtin \
         -fno-pic -fno-pie -nostdlib -nostdinc -w -c

LFLAGS = -m elf_i386 -T linker.ld --oformat binary

.PHONY: all clean run run-nographic

all: prepare $(BUILD_DIR)/os.img
	@echo ""
	@echo "  MaxOS compile !"
	@echo "  make run pour lancer"
	@echo ""

prepare:
	@mkdir -p $(BUILD_DIR)

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

$(BUILD_DIR)/idt.o: kernel/idt.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/timer.o: kernel/timer.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/memory.o: kernel/memory.c
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/vga.o: drivers/vga.c
	$(CC) $(CFLAGS) $< -o $@

KERNEL_OBJS := $(BUILD_DIR)/kernel_entry.o \
               $(BUILD_DIR)/kernel.o \
               $(BUILD_DIR)/screen.o \
               $(BUILD_DIR)/keyboard.o \
               $(BUILD_DIR)/ui.o \
               $(BUILD_DIR)/notepad.o \
               $(BUILD_DIR)/terminal.o \
               $(BUILD_DIR)/sysinfo.o \
               $(BUILD_DIR)/about.o

IDT_SRC    := $(wildcard kernel/idt.c)
TIMER_SRC  := $(wildcard kernel/timer.c)
MEMORY_SRC := $(wildcard kernel/memory.c)
VGA_SRC    := $(wildcard drivers/vga.c)

ifneq ($(IDT_SRC),)
KERNEL_OBJS += $(BUILD_DIR)/idt.o
endif
ifneq ($(TIMER_SRC),)
KERNEL_OBJS += $(BUILD_DIR)/timer.o
endif
ifneq ($(MEMORY_SRC),)
KERNEL_OBJS += $(BUILD_DIR)/memory.o
endif
ifneq ($(VGA_SRC),)
KERNEL_OBJS += $(BUILD_DIR)/vga.o
endif

$(BUILD_DIR)/kernel.bin: $(KERNEL_OBJS)
	$(LD) $(LFLAGS) $^ -o $@

$(BUILD_DIR)/os.img: $(BUILD_DIR)/boot.bin $(BUILD_DIR)/kernel.bin
	@echo "Construction image disque..."
	@KERNEL_SIZE=$$(wc -c < $(BUILD_DIR)/kernel.bin); \
	 SECTORS=$$(( (KERNEL_SIZE + 511) / 512 )); \
	 echo "  Kernel: $$KERNEL_SIZE bytes = $$SECTORS secteurs"; \
	 if [ $$SECTORS -gt 2879 ]; then \
	   echo "ERREUR: Kernel trop grand ($$SECTORS secteurs > 2879)"; \
	   exit 1; \
	 fi; \
	 echo "  Secteurs OK: $$SECTORS"
	@cat $(BUILD_DIR)/boot.bin $(BUILD_DIR)/kernel.bin > $(BUILD_DIR)/os.img
	@truncate -s 1474560 $(BUILD_DIR)/os.img
	@echo "Image creee: $(BUILD_DIR)/os.img"

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

clean:
	@rm -rf $(BUILD_DIR)
	@echo "Nettoyage termine"