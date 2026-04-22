ENTRY(_start)
OUTPUT_FORMAT(binary)

SECTIONS
{
    . = 0x10000;
    .text   : { *(.text) }
    .data   : { *(.data) }
    .rodata : { *(.rodata) }
    .bss    : { *(.bss) *(COMMON) }
}