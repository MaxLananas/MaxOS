# Ce Makefile est inclus dans le Makefile principal
# Il gère uniquement les fichiers du noyau
VPATH = ../

SRCS_C = \
	idt.c \
	irq.c \
	irq_handler.c \
	timer.c \
	memory.c \
	fault_handler.c \
	paging.c \
	screen.c \
	keyboard.c \
	terminal.c \
	mouse.c \
	kmain.c

OBJS = \
	$(addprefix $(BUILD)/, $(SRCS_C:.c=.o))

$(BUILD)/%.o: kernel/%.c | $(BUILD)
	$(CC) $(CFLAGS) -c $< -o $@