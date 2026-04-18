ENTRY(_start)
SECTIONS {
    . = 0x8000;
    .text : { *(.text) }
    .data : { *(.data) }
    .bss  : { *(.bss)  }
    .stack : {
        . = ALIGN(4);
        _stack_bottom = .;
        . += 16K;
        _stack_top = .;
    }
}