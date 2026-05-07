ENTRY(_start)

SECTIONS
{
    . = 0x1000;

    .text : {
        *(.text*)
    }

    .data : {
        *(.data*)
        *(.rodata*)
    }

    .bss : {
        *(.bss*)
    }

    /DISCARD/ : {
        *(.comment*)
        *(.eh_frame*)
        *(.note*)
    }

    _stack_top = . + 16384;
}