# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

```markdown
# **MaxOS – Documentation Technique**
*Un système d'exploitation minimaliste en développement*

---
**Version** : 0.1 (Pre-Alpha)
**Score** : 35/100 (Fonctionnalités de base implémentées)
**Licence** : MIT
**Auteurs** : [Votre Nom/Groupe]
**Dernière mise à jour** : [Date]

---

## **1. Introduction**
MaxOS est un système d'exploitation **32-bit** en développement, conçu pour des architectures **x86**. Il intègre actuellement :
- Un **bootloader** fonctionnel (`boot.asm`).
- Une **IDT** (Interrupt Descriptor Table) initialisée (`idt.c/idt.asm`).
- Des **ISR** (Interrupt Service Routines) manuelles (`isr.asm`).
- La gestion des **IRQ/PIT** (Interruptions matérielles et timer, `irq.asm/timer.c`).
- Une **gestion mémoire basique** (physique et virtuelle, `pmm.c/vmm.c`).
- Un **pilote VGA** pour l'affichage texte (`screen.c`).
- Un **pilote clavier PS/2** (`keyboard.c`).
- Un **terminal minimaliste** (`terminal.c`).

---
## **2. Prérequis et Compilation**

### **2.1. Dépendances**
Pour compiler MaxOS, vous aurez besoin de :
- **GCC** (pour la compilation croisée, `i686-elf-gcc`).
- **NASM** (assembleur, version ≥ 2.15).
- **GNU Make** (pour l'automatisation).
- **QEMU** (pour l'émulation, version ≥ 6.0).
- **GNU Grub** (pour générer l'image disque, `grub-mkrescue`).

#### **Installation sous Linux (Debian/Ubuntu)**
```bash
sudo apt update
sudo apt install build-essential nasm qemu-system-x86 grub2 xorriso
```

#### **Installation du compilateur croisé (i686-elf)**
```bash
# Télécharger et installer le toolchain (exemple pour Linux)
wget https://github.com/lordmilko/i686-elf-tools/releases/download/8.3/i686-elf-tools-linux.tar.xz
tar -xf i686-elf-tools-linux.tar.xz
sudo mv i686-elf-tools /opt/
export PATH="$PATH:/opt/i686-elf-tools/bin"
```

---

### **2.2. Compilation**
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/[votre-utilisateur]/MaxOS.git
   cd MaxOS
   ```

2. **Compiler le noyau** :
   ```bash
   make
   ```
   - Cela génère :
     - `bin/kernel.bin` (binaire du noyau).
     - `bin/os.iso` (image bootable avec GRUB).

3. **Nettoyer les fichiers temporaires** :
   ```bash
   make clean
   ```

---
## **3. Test avec QEMU**

### **3.1. Lancer l'OS en mode graphique**
```bash
make run
```
- **Options QEMU** :
  - `-m 512M` : 512 Mo de RAM.
  - `-serial mon:stdio` : Redirige la sortie série vers le terminal.
  - `-d int` : Affiche les interruptions (débogage).

### **3.2. Débogage avec GDB**
1. Lancer QEMU en mode débogage :
   ```bash
   make debug
   ```
2. Dans un autre terminal, attacher GDB :
   ```bash
   i686-elf-gdb bin/kernel.bin
   (gdb) target remote localhost:1234
   (gdb) continue
   ```

### **3.3. Captures d'écran**
- **Sortie attendue** :
  - Affichage du message de boot (`"MaxOS v0.1"`).
  - Terminal interactif (saisie clavier fonctionnelle).
  - Timer PIT affichant des interruptions périodiques.

---
## **4. Structure des Fichiers**

```
MaxOS/
├── bin/                # Binaires générés (kernel.bin, os.iso)
├── src/
│   ├── boot/           # Bootloader (boot.asm, multiboot.h)
│   ├── kernel/         # Noyau principal
│   │   ├── cpu/        # Gestion CPU (idt.c, isr.asm, irq.asm)
│   │   ├── mem/        # Mémoire (pmm.c, vmm.c, heap.c)
│   │   ├── drivers/    # Pilotes (screen.c, keyboard.c)
│   │   ├── terminal/   # Terminal (terminal.c)
│   │   └── init/       # Initialisation (main.c, kernel_entry.asm)
│   └── lib/            # Bibliothèques utilitaires (stdio.h, string.c)
├── tools/              # Scripts (grub.mk, link.ld)
├── Makefile            # Règles de compilation
└── docs/               # Documentation
```

### **Fichiers clés**
| Fichier               | Rôle                                  |
|-----------------------|---------------------------------------|
| `boot/boot.asm`       | Bootloader (mode réel → protégé).     |
| `kernel/cpu/idt.c`    | Initialisation de l'IDT.             |
| `kernel/cpu/isr.asm`  | Handlers d'interruptions.             |
| `kernel/mem/pmm.c`    | Gestionnaire de mémoire physique.    |
| `kernel/drivers/screen.c` | Pilote VGA (texte 80x25).       |
| `kernel/terminal/terminal.c` | Interface utilisateur basique. |

---
## **5. Contribuer au Projet**

### **5.1. Rapporter un Bug**
- Ouvrir une **issue** sur GitHub avec :
  - Une description claire.
  - Les étapes pour reproduire.
  - La sortie de `make run` (logs).

### **5.2. Soumettre une Pull Request (PR)**
1. **Forker** le dépôt.
2. Créer une branche :
   ```bash
   git checkout -b feature/[nom]
   ```
3. Commiter avec des messages clairs :
   ```bash
   git commit -m "feat(mem): Ajout de la pagination"
   ```
4. Pousser et ouvrir une PR vers `main`.

### **5.3. Conventions de Code**
- **C** : Norme **C99** (pas de C++).
- **Assembleur** : Syntax **NASM**.
- **Nommage** :
  - `snake_case` pour les fonctions/variables.
  - `SCREAMING_SNAKE_CASE` pour les macros.
- **Commentaires** :
  - **Doxygen** pour les fonctions publiques.
  - Explications pour les sections critiques (ex : `pmm.c`).

---
## **6. Roadmap**

| Version | Objectifs                                                                 | Statut      |
|---------|---------------------------------------------------------------------------|-------------|
| **0.1** | Bootloader, IDT, ISR, PIT, VGA, Clavier, Terminal basique.               | ✅ Terminé  |
| **0.2** | Gestion avancée de la mémoire (paging, heap), Système de fichiers (FAT16). | ⚠️ En cours |
| **0.3** | Multitâche (scheduler round-robin), Pilotes ATA/IDE.                     | ❌ Planifié  |
| **0.4** | Réseau (pilote NE2000), GUI basique (VESA).                              | ❌ Planifié  |
| **1.0** | Version stable avec shell utilisable.                                    | ❌ Long terme |

### **Prochaines Étapes (Priorité)**
1. **Implémenter le paging** (`vmm.c`).
2. **Ajouter un allocateur dynamique** (`heap.c`).
3. **Support des appels système** (`syscall.asm`).
4. **Pilote ATA** pour lire le disque.

---
## **7. Ressources Utiles**
- **Documentation x86** :
  - [Intel Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
  - [OSDev Wiki](https://wiki.osdev.org/)
- **Outils** :
  - [QEMU Monitor Commands](https://wiki.qemu.org/Documentation/Monitor)
  - [GDB for OSDev](https://wiki.osdev.org/Kernel_Debugging)

---
## **8. Licence**
Ce projet est sous **licence MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

---
**Contact** : [votre

---
*MaxOS AI v18.0*
