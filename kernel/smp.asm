BITS 32

section .text
global ap_start

ap_start:
    ; Code de démarrage des AP (Application Processors)
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax

    ; Charger la pile du CPU
    mov esp, ebx

    ; Appeler la fonction d'initialisation
    call smp_ap_init

    ; Boucle infinie si retour
    cli
    hlt
    jmp $

smp_ap_init:
    ; Initialisation spécifique pour les AP
    call apic_enable
    call smp_ap_main
    ret