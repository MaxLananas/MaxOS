[BITS 32]

; Déclarations des fonctions C
extern kernel_main
extern exception_handler
extern pic_send_eoi ; Pour les IRQ

; ==============================================================================
; Macros pour les gestionnaires d'interruptions (ISR)
; ==============================================================================

; Macro pour les exceptions qui ne poussent PAS de code d'erreur sur la pile
%macro ISR_NOERRCODE 1
    global isr%1
    isr%1:
        cli                 ; Désactiver les interruptions (par sécurité)
        push byte 0         ; Pousser un code d'erreur factice (0)
        push byte %1        ; Pousser le numéro de l'interruption
        jmp isr_common_stub
%endmacro

; Macro pour les exceptions qui poussent un code d'erreur sur la pile
%macro ISR_ERRCODE 1
    global isr%1
    isr%1:
        cli                 ; Désactiver les interruptions (par sécurité)
        ; Le code d'erreur est déjà poussé par le CPU
        push byte %1        ; Pousser le numéro de l'interruption
        jmp isr_common_stub
%endmacro

; Macro pour les gestionnaires d'IRQ
%macro IRQ 2
    global irq%1
    irq%1:
        cli                 ; Désactiver les interruptions
        push byte 0         ; Pousser un code d'erreur factice (0)
        push byte %2        ; Pousser le numéro de l'interruption (remappé)
        jmp irq_common_stub
%endmacro

; ==============================================================================
; Définition des 32 exceptions x86
; ==============================================================================

ISR_NOERRCODE 0   ; Division By Zero Exception
ISR_NOERRCODE 1   ; Debug Exception
ISR_NOERRCODE 2   ; Non-Maskable Interrupt Exception
ISR_NOERRCODE 3   ; Breakpoint Exception
ISR_NOERRCODE 4   ; Overflow Exception
ISR_NOERRCODE 5   ; Bound Range Exceeded Exception
ISR_NOERRCODE 6   ; Invalid Opcode Exception
ISR_NOERRCODE 7   ; Device Not Available Exception
ISR_ERRCODE   8   ; Double Fault Exception
ISR_NOERRCODE 9   ; Coprocessor Segment Overrun (Reserved)
ISR_ERRCODE   10  ; Invalid TSS Exception
ISR_ERRCODE   11  ; Segment Not Present Exception
ISR_ERRCODE   12  ; Stack-Segment Fault Exception
ISR_ERRCODE   13  ; General Protection Fault Exception
ISR_ERRCODE   14  ; Page Fault Exception
ISR_NOERRCODE 15  ; Reserved
ISR_NOERRCODE 16  ; x87 Floating-Point Exception
ISR_ERRCODE   17  ; Alignment Check Exception
ISR_NOERRCODE 18  ; Machine Check Exception
ISR_NOERRCODE 19  ; SIMD Floating-Point Exception
ISR_NOERRCODE 20  ; Virtualization Exception
ISR_ERRCODE   21  ; Control Protection Exception
ISR_NOERRCODE 22  ; Reserved
ISR_NOERRCODE 23  ; Reserved
ISR_NOERRCODE 24  ; Reserved
ISR_NOERRCODE 25  ; Reserved
ISR_NOERRCODE 26  ; Reserved
ISR_NOERRCODE 27  ; Reserved
ISR_NOERRCODE 28  ; Reserved
ISR_NOERRCODE 29  ; Reserved
ISR_NOERRCODE 30  ; Reserved
ISR_NOERRCODE 31  ; Reserved

; ==============================================================================
; Définition des 16 IRQ remappées (32-47)
; ==============================================================================

IRQ 0, 32   ; IRQ0 (Timer)
IRQ 1, 33   ; IRQ1 (Keyboard)
IRQ 2, 34   ; IRQ2 (PIC cascade)
IRQ 3, 35   ; IRQ3 (COM2)
IRQ 4, 36   ; IRQ4 (COM1)
IRQ 5, 37   ; IRQ5 (LPT2/Sound Card)
IRQ 6, 38   ; IRQ6 (Floppy Disk)
IRQ 7, 39   ; IRQ7 (LPT1/Spurious)
IRQ 8, 40   ; IRQ8 (RTC)
IRQ 9, 41   ; IRQ9 (Redirected IRQ2)
IRQ 10, 42  ; IRQ10 (Reserved)
IRQ 11, 43  ; IRQ11 (Reserved)
IRQ 12, 44  ; IRQ12 (PS/2 Mouse)
IRQ 13, 45  ; IRQ13 (FPU)
IRQ 14, 46  ; IRQ14 (Primary ATA)
IRQ 15, 47  ; IRQ15 (Secondary ATA)

; ==============================================================================
; Stub commun pour les exceptions (ISR)
; ==============================================================================
isr_common_stub:
    push eax
    push ecx
    push edx
    push ebx
    push esp    ; Pousser ESP avant EBP pour le passer au handler C
    push ebp
    push esi
    push edi

    ; Appeler le gestionnaire C
    call exception_handler

    ; Restaurer les registres
    pop edi
    pop esi
    pop ebp
    add esp, 4  ; Retirer l'ESP factice
    pop ebx
    pop edx
    pop ecx
    pop eax

    add esp, 8  ; Retirer le numéro d'interruption et le code d'erreur
    sti         ; Réactiver les interruptions (si le handler C ne panique pas)
    iret        ; Retour de l'interruption

; ==============================================================================
; Stub commun pour les IRQ
; ==============================================================================
irq_common_stub:
    push eax
    push ecx
    push edx
    push ebx
    push esp    ; Pousser ESP avant EBP pour le passer au handler C
    push ebp
    push esi
    push edi

    ; Appeler le gestionnaire C (pour l'instant, il gère aussi les IRQ comme des exceptions)
    ; Plus tard, on aura un handler_irq spécifique
    call exception_handler ; Pour l'instant, on utilise le même handler pour voir les IRQ

    ; Envoyer l'EOI au PIC
    ; Le numéro d'IRQ est sur la pile à [esp + 8] (après les registres et le code d'erreur)
    mov al, [esp + 8 + 4*8] ; int_no est à (esp_after_pusha + 8)
    sub al, 32              ; Convertir le numéro d'interruption en numéro d'IRQ (0-15)
    push eax                ; Pousser le numéro d'IRQ comme argument
    call pic_send_eoi
    add esp, 4              ; Nettoyer l'argument

    ; Restaurer les registres
    pop edi
    pop esi
    pop ebp
    add esp, 4  ; Retirer l'ESP factice
    pop ebx
    pop edx
    pop ecx
    pop eax

    add esp, 8  ; Retirer le numéro d'interruption et le code d'erreur
    sti         ; Réactiver les interruptions
    iret        ; Retour de l'interruption

; ==============================================================================
; Point d'entrée du kernel
; ==============================================================================
global _start
_start:
    ; Initialisation des segments de données (DS, ES, FS, GS, SS)
    ; Le sélecteur de segment de données du kernel est 0x10
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax

    ; Initialisation de la pile
    ; La pile est définie par le linker.ld à la fin de la section .bss
    ; On la met à la fin de la mémoire disponible pour le kernel (0x8000 + taille_kernel)
    ; Pour l'instant, on peut la laisser à l'adresse par défaut du linker.ld
    ; ou la définir explicitement si nécessaire.
    ; Pour ce projet, le linker.ld gère déjà la pile.

    call kernel_main ; Appel de la fonction principale du kernel en C

    cli ; Désactiver les interruptions
    hlt ; Arrêter le CPU