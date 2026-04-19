ASM = nasm
CC = gcc
LD = ld
QEMU = qemu-system-i386

BUILD_DIR = build

CFLAGS = -m32 -ffreestanding -fno-stack-protector -fno-builtin \
         -fno-pic -fno-pie -nostdlib -nostdinc -w -c

LFLAGS = -m elf_i386 -T linker.ld --oformat binary

.PHONY: all clean run run-nographic prepare


all: os.img
	@echo ""
	@echo "  MaxOS compile !"
	@echo "  make run pour lancer"
	@echo ""

prepare:
	@mkdir -p $(BUILD_DIR)


$(BUILD_DIR)/boot.bin: boot/boot.asm | prepare
	$(ASM) -f bin $< -o $@


$(BUILD_DIR)/kernel_entry.o: kernel/kernel_entry.asm | prepare
	$(ASM) -f elf $< -o $@

$(BUILD_DIR)/isr.o: kernel/isr.asm | prepare
	$(ASM) -f elf $< -o $@


$(BUILD_DIR)/kernel.o: kernel/kernel.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/idt.o: kernel/idt.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/isr_c.o: kernel/isr.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/timer.o: kernel/timer.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/memory.o: kernel/memory.c | prepare
	$(CC) $(CFLAGS) $< -o $@


$(BUILD_DIR)/screen.o: drivers/screen.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/keyboard.o: drivers/keyboard.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/vga.o: drivers/vga.c | prepare
	$(CC) $(CFLAGS) $< -o $@


$(BUILD_DIR)/ui.o: ui/ui.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/notepad.o: apps/notepad.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/terminal.o: apps/terminal.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/sysinfo.o: apps/sysinfo.c | prepare
	$(CC) $(CFLAGS) $< -o $@

$(BUILD_DIR)/about.o: apps/about.c | prepare
	$(CC) $(CFLAGS) $< -o $@


KERNEL_OBJS := $(BUILD_DIR)/kernel_entry.o \
               $(BUILD_DIR)/kernel.o \
               $(BUILD_DIR)/screen.o \
               $(BUILD_DIR)/keyboard.o \
               $(BUILD_DIR)/ui.o \
               $(BUILD_DIR)/notepad.o \
               $(BUILD_DIR)/terminal.o \
               $(BUILD_DIR)/sysinfo.o \
               $(BUILD_DIR)/about.o \
               $(BUILD_DIR)/idt.o \
               $(BUILD_DIR)/isr.o \
               $(BUILD_DIR)/isr_c.o \
               $(BUILD_DIR)/timer.o \
               $(BUILD_DIR)/memory.o \
               $(BUILD_DIR)/vga.o

$(BUILD_DIR)/kernel.bin: $(KERNEL_OBJS)
	$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD_DIR)/boot.bin $(BUILD_DIR)/kernel.bin
	@echo "Construction image disque..."
	dd if=/dev/zero of=os.img bs=512 count=2880
	dd if=$(BUILD_DIR)/boot.bin of=os.img conv=notrunc
	dd if=$(BUILD_DIR)/kernel.bin of=os.img seek=1 conv=notrunc
	@echo "Image creee: os.img"

run: os.img
	$(QEMU) \
		-drive format=raw,file=os.img,if=floppy \
		-boot a \
		-vga std \
		-k fr \
		-m 32 \
		-no-fd-bootchk \
		-no-reboot

run-nographic: os.img
	$(QEMU) \
		-drive format=raw,file=os.img,if=floppy \
		-boot a \
		-nographic \
		-no-reboot

clean:
	@rm -rf $(BUILD_DIR) os.img
	@echo "Nettoyage termine"
