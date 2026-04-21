# Architecture MaxOS

## Fonctions canoniques

| Fonction | Signature |
|---|---|
| `screen_init` | `void screen_init(void)` |
| `screen_clear` | `void screen_clear(void)` |
| `screen_putchar` | `void screen_putchar(char c, unsigned char color)` |
| `screen_write` | `void screen_write(const char *str, unsigned char color)` |
| `screen_writeln` | `void screen_writeln(const char *str, unsigned char color)` |
| `screen_set_color` | `void screen_set_color(unsigned char color)` |
| `screen_get_row` | `int screen_get_row(void)` |
| `screen_scroll` | `void screen_scroll(void)` |
| `keyboard_init` | `void keyboard_init(void)` |
| `keyboard_getchar` | `char keyboard_getchar(void)` |
| `keyboard_handler` | `void keyboard_handler(void)` |
| `idt_init` | `void idt_init(void)` |
| `idt_set_gate` | `void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags)` |
| `isr_handler` | `void isr_handler(unsigned int num, unsigned int err)` |
| `irq_handler` | `void irq_handler(unsigned int num)` |
| `timer_init` | `void timer_init(unsigned int hz)` |
| `timer_get_ticks` | `unsigned int timer_get_ticks(void)` |
| `timer_sleep` | `void timer_sleep(unsigned int ms)` |
| `mem_init` | `void mem_init(unsigned int mem_size_kb)` |
| `mem_alloc_page` | `void *mem_alloc_page(void)` |
| `mem_free_page` | `void mem_free_page(void *addr)` |
| `mem_used_pages` | `unsigned int mem_used_pages(void)` |
| `heap_init` | `void heap_init(void *start, unsigned int size)` |
| `heap_alloc` | `void *heap_alloc(unsigned int size)` |
| `heap_free` | `void heap_free(void *ptr)` |
| `kmain` | `void kmain(void)` |
| `terminal_init` | `void terminal_init(void)` |
| `terminal_run` | `void terminal_run(void)` |
| `terminal_process` | `void terminal_process(const char *cmd)` |
| `mouse_init` | `void mouse_init(void)` |
| `mouse_handler` | `void mouse_handler(void)` |
| `fault_handler` | `void fault_handler(unsigned int num, unsigned int err)` |
| `paging_init` | `void paging_init(void)` |
| `paging_map` | `void paging_map(unsigned int virt, unsigned int phys, unsigned int flags)` |

## Fonctions implémentées (108)

| Fonction | Fichier | Signature |
|---|---|---|
| `ab_draw` | — | `void ab_draw(void);` |
| `ab_key` | — | `;` |
| `np_init` | — | `void np_init(void);` |
| `np_draw` | — | `;` |
| `np_key` | — | `;` |
| `si_draw` | — | `void si_draw(void);` |
| `si_key` | — | `;` |
| `tm_init` | — | `void tm_init(void);` |
| `tm_draw` | — | `;` |
| `tm_key` | — | `;` |
| `tm_scroll_up` | — | `;` |
| `tm_print` | — | `;` |
| `tm_print_char` | — | `;` |
| `tm_execute_command` | — | `;` |
| `tm_draw_input_line` | — | `;` |
| `tm_set_cursor` | — | `;` |
| `tm_beep` | — | `;` |
| `tm_str_len` | — | `;` |
| `tm_str_cmp` | — | `;` |
| `tm_str_cpy` | — | `;` |
| `tm_str_cat` | — | `;` |
| `tm_mem_set` | — | `;` |
| `tm_mem_cpy` | — | `;` |
| `tm_int_to_str` | — | `;` |
| `tm_int_to_str_padded` | — | `;` |
| `tm_int_to_hex_str` | — | `;` |
| `tm_str_to_int` | — | `;` |
| `tm_parse_arg` | — | `;` |
| `kb_init` | — | `void kb_init(void);` |
| `kb_haskey` | — | `;` |

## Règles bare metal

```
╔══ RÈGLES BARE METAL x86 — VIOLATIONS = ÉCHEC BUILD ══╗
║ INCLUDES INTERDITS: stddef.h string.h stdlib.h stdio.h║
║   stdint.h stdbool.h stdarg.h stdnoreturn.h            ║
║ SYMBOLES INTERDITS: size_t NULL bool true false        ║
║   uint32_t uint8_t uint16_t int32_t                    ║
║   malloc free calloc realloc                           ║
║   memset memcpy memmove strlen strcpy strcat           ║
║   printf sprintf fprintf puts                          ║
║ REMPLACEMENTS: size_t→unsigned int  NULL→0             ║
║   bool/true/false→int/1/0  uint32_t→unsigned int      ║
║   uint8_t→unsigned char  uint16_t→unsigned short      ║
║ TOOLCHAIN:                                             ║
║   GCC: -m32 -ffreestanding -fno-builtin               ║
║        -nostdlib -nostdinc -fno-pic -fno-pie           ║
║   NASM: -f elf (→.o) | -f bin (boot.bin)              ║
║   LD: ld -m elf_i386 -T linker.ld --oformat binary    ║
║ RÈGLES CRITIQUES:                                      ║
║   • kernel/io.h: SEUL fichier avec outb/inb            ║
║   • isr.asm: PAS de %macro/%rep — ÉCRIRE isr0:...     ║
║     isr47: MANUELLEMENT, un par un                     ║
║   • kernel_entry.asm: appelle 'kmain' (pas 'main')    ║
║   • Tout .c nouveau → Makefile OBJS                   ║
║   • ZÉRO commentaire dans le code                     ║
║   • os.img via: dd boot.bin + dd kernel.bin seek=1    ║
║   • NE PAS utiliser 'unsigned_char' (typo fréquente)  ║
║   • EN MODE 32BIT: pas de 'push eip' ou '%eip'        ║
║   • NE PAS inventer: v_put v_str kernel_main           ║
╚════════════════════════════════════════════════════════╝
```

---
*MaxOS AI v18.0*
