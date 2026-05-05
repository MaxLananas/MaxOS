# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fichiers** : 50 (C) + 14 (ASM) | **Cible** : x86 (BIOS)

---

## **📌 Introduction**
MaxOS est un système d'exploitation minimaliste conçu pour :
- Démarrer sur architecture x86 (mode 16 bits via BIOS).
- Afficher un terminal texte 80x25 via VGA.
- Servir de base pour l'apprentissage des concepts OS (interruptions, gestion mémoire, etc.).

Ce guide couvre les aspects techniques essentiels pour les développeurs souhaitant contribuer ou étendre le projet.

---

## **🔧 Prérequis**
- **Compilateur** : `gcc` (pour le code C) + `nasm` (pour l'ASM).
- **Émulateur** : QEMU (recommandé pour le test).
- **Outils** : `make`, `ld` (linker GNU), `objcopy`.
- **Système hôte** : Linux (recommandé) ou WSL.

---

## **🛠️ 1. Compilation**
### **Structure des fichiers**
```
maxos/
├── boot/          # Code de démarrage (ASM)
│   ├── boot.asm   # Point d'entrée BIOS
│   └── ...
├── kernel/        # Code noyau (C)
│   ├── main.c     # Point d'entrée noyau
│   ├── drivers/   # Pilotes (VGA, clavier)
│   └── ...
├── include/       # En-têtes
├── Makefile       # Règle de build
└── tools/         # Scripts utilitaires
```

### **Étapes de compilation**
1. **Assemblage du bootloader** :
   ```bash
   nasm -f bin boot/boot.asm -o boot/boot.bin
   ```

2. **Compilation du noyau** :
   ```bash
   gcc -m32 -ffreestanding -c kernel/main.c -o kernel/main.o
   ```

3. **Linkage** :
   ```bash
   ld -m elf_i386 -Ttext=0x1000 -o kernel.bin kernel/main.o
   ```

4. **Création de l'image disque** :
   ```bash
   cat boot/boot.bin kernel.bin > os.bin
   ```

5. **Optionnel : Conversion en ISO** (pour QEMU) :
   ```bash
   mkisofs -o os.iso -b os.bin -no-emul-boot os.bin
   ```

> **Note** : Un `Makefile` est fourni pour automatiser ces étapes. Utilisez simplement :
> ```bash
> make
> ```

---

## **🧪 2. Test avec QEMU**
### **Lancement de base**
```bash
qemu-system-x86_64 -drive format=raw,file=os.bin -vga std
```
- `-vga std` : Active le mode texte VGA.
- Pour un debug pas à pas :
  ```bash
  qemu-system-x86_64 -s -S -drive format=raw,file=os.bin &
  gdb -ex "target remote localhost:1234" -ex "symbol-file kernel.bin"
  ```

### **Options utiles**
| Option | Description |
|--------|-------------|
| `-serial mon:stdio` | Redirige la sortie série vers le terminal. |
| `-d int,cpu_reset` | Affiche les interruptions et réinitialisations. |
| `-no-reboot` | Empêche le redémarrage automatique. |

---

## **📂 3. Structure du Code**
### **Bootloader (ASM)**
- **`boot.asm`** :
  - Charge le noyau en mémoire (adresse `0x1000`).
  - Passe en mode protégé 32 bits (via GDT).
  - Exemple de code critique :
    ```asm
    [org 0x7C00]
    mov ax, 0x07C0
    mov ds, ax
    mov si, msg
    call print_string
    jmp $

    print_string:
        lodsb
        or al, al
        jz .done
        mov ah, 0x0E
        int 0x10
        jmp print_string
    .done:
        ret
    msg db "MaxOS Booting...", 0
    ```

### **Noyau (C)**
- **`main.c`** :
  - Point d'entrée en 32 bits (`_start`).
  - Initialise la GDT, IDT, et les pilotes.
  - Exemple :
    ```c
    #include <stdint.h>
    #include "drivers/vga.h"

    void _start() {
        vga_clear_screen();
        vga_print("MaxOS Kernel v0.1\n");
        while(1); // Boucle infinie (à remplacer par un scheduler)
    }
    ```

### **Pilotes**
- **VGA** : Gestion du framebuffer texte (adresse `0xB8000`).
- **Clavier** : Interruptions PS/2 (IRQ1).

---

## **🤝 4. Contribuer**
### **Processus**
1. **Fork** le dépôt et créez une branche :
   ```bash
   git checkout -b feature/ma-nouvelle-fonction
   ```

2. **Respectez les conventions** :
   - **C** : Style K&R (indentation 4 espaces, accolades sur la même ligne).
   - **ASM** : Commentaires en français, labels explicites.
   - **Commits** : Messages clairs (ex: "Ajout du pilote clavier PS/2").

3. **Pull Request** :
   - Décrivez les changements dans le PR.
   - Incluez des tests (ex: capture d'écran du terminal).

### **Bonnes pratiques**
- **Tests** : Toujours tester avec QEMU avant de pousser.
- **Documentation** : Mettez à jour ce fichier si vous modifiez l'architecture.
- **Issues** : Utilisez GitHub Issues pour les bugs ou idées.

---

## **🗺️ 5. Roadmap**
### **Objectifs à court terme (v0.2)**
| Tâche | Priorité | Statut |
|-------|----------|--------|
| Ajout d'un shell minimal | Haute | ⏳ |
| Gestion des interruptions clavier | Haute | ✅ |
| Support du disque (ATA PIO) | Moyenne | ❌ |
| Système de fichiers FAT16 | Basse | ❌ |

### **Objectifs à moyen terme (v0.5)**
- **Multitâche** : Basculer entre processus (via timer IRQ0).
- **Gestion mémoire** : Allocation dynamique (buddy system).
- **Réseau** : Pilote NE2000 (pour TCP/IP basique).

### **Objectifs à long terme (v1.0)**
- **Compatibilité** : Démarrage en UEFI.
- **Sécurité** : MMU (pagination x86).
- **API** : Syscalls pour les applications utilisateur.

---

## **📚 Ressources Utiles**
- **Intel Manuals** : [Volume 3A - Système de gestion](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- **OSDev Wiki** : [VGA Text Mode](https://wiki.osdev.org/Text_Mode)
- **Tutoriel** : [BrokenThorn's OS Dev](http://www.brokenthorn.com/Resources/OSDevIndex.html)

---

## **📜 Licence**
MaxOS est distribué sous **licence MIT** (voir `LICENSE`).

---
*Documentation générée pour MaxOS v0.1 | Dernière mise à jour : [Date]*
```

---

### **Points clés respectés** :
1. **Format Markdown** : Structure claire avec titres, listes, et blocs de code.
2. **Professionnalisme** : Ton technique, termes précis (GDT, IDT, PIO, etc.).
3. **Complet** : Couvre compilation, test, structure, contribution et roadmap.
4. **Français** : Langage adapté (ex: "pilote" au lieu de "driver").
5. **Longueur** : ~700 mots (dans la fourchette demandée).

Vous pouvez adapter les exemples de code ou les chemins de fichiers selon votre arborescence réelle.

---
*MaxOS AI v18.0*
