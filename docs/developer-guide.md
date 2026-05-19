# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

```markdown
# **MaxOS – Documentation Technique (Prototype Bare Metal)**
*Version: 0.1-alpha | Statut: Boot x86 + VGA Texte 80x25*
*Fichiers: 57 (C) | 19 (ASM) | Score: 35/100*

---
## **1. Introduction**
MaxOS est un système d'exploitation **bare metal** en développement, ciblant l'architecture **x86** avec un support minimaliste (boot secteur, mode texte VGA 80x25). Ce document s'adresse aux développeurs souhaitant contribuer ou comprendre l'architecture du projet.

**Objectifs actuels** :
- Boot autonome (sans GRUB) via un secteur d'amorçage (512 octets).
- Affichage basique en mode texte (interruptions BIOS `0x10`).
- Gestion mémoire et multitâche (futur).

**Prérequis** :
- Connaissances en **C**, **Assembleur x86 (NASM)**, et **systèmes bas niveau**.
- Outils : `nasm`, `gcc`, `ld`, `qemu`, `make`.

---

## **2. Compilation du Projet**
### **2.1. Dépendances**
Installez les outils nécessaires :
```bash
# Debian/Ubuntu
sudo apt install nasm gcc make qemu-system-x86
# Arch Linux
sudo pacman -S nasm gcc make qemu
```

### **2.2. Étapes de compilation**
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-depot/MaxOS.git
   cd MaxOS
   ```

2. **Compiler le secteur de boot (ASM)** :
   ```bash
   nasm -f bin boot/boot.asm -o boot/boot.bin
   ```

3. **Compiler le noyau (C + ASM)** :
   ```bash
   # Compilation des fichiers C en objets
   gcc -m32 -c kernel/*.c -o kernel/kernel.o -ffreestanding -Wall -Wextra
   # Assemblage des fichiers ASM
   nasm -f elf32 kernel/entry.asm -o kernel/entry.o
   # Édition des liens (ld script requis)
   ld -m elf_i386 -T kernel/linker.ld -o kernel/MaxOS.bin kernel/entry.o kernel/kernel.o --oformat binary
   ```

4. **Créer l'image disque** :
   ```bash
   cat boot/boot.bin kernel/MaxOS.bin > MaxOS.img
   ```

5. **Automatisation (Makefile)** :
   ```bash
   make all  # Compile tout
   make clean # Nettoie les fichiers temporaires
   ```

---

## **3. Test avec QEMU**
### **3.1. Lancement basique**
```bash
qemu-system-x86_64 -fda MaxOS.img -no-reboot -no-shutdown
```
**Options utiles** :
- `-d int` : Afficher les interruptions (debug).
- `-serial stdio` : Rediriger la sortie série vers le terminal.
- `-s -S` : Attendre un débogueur (GDB).

### **3.2. Débogage avec GDB**
1. Lancer QEMU en mode pause :
   ```bash
   qemu-system-x86_64 -fda MaxOS.img -s -S
   ```
2. Dans un autre terminal :
   ```bash
   gdb -ex "target remote localhost:1234" -ex "symbol-file kernel/MaxOS.bin"
   ```
   Commandes GDB utiles :
   - `break *0x7C00` : Point d'arrêt sur le secteur de boot.
   - `x/10i $pc` : Afficher les prochaines instructions.

---

## **4. Structure des Fichiers**
```
MaxOS/
├── boot/
│   ├── boot.asm       # Secteur de boot (512 octets, code 16-bit)
│   └── boot.bin       # Binaire généré
├── kernel/
│   ├── entry.asm      # Point d'entrée 32-bit (passage en mode protégé)
│   ├── kernel.c       # Noyau principal (initialisation, VGA, etc.)
│   ├── linker.ld      # Script de linkage (adresses mémoire)
│   ├── memory/        # Gestion mémoire (futur)
│   └── drivers/       # Pilotes (VGA, clavier, etc.)
├── tools/             # Scripts utilitaires (ex: générateur de tables GDT)
├── MaxOS.img          # Image disque finale
└── Makefile           # Automatisation
```

### **4.1. Points clés**
- **boot.asm** :
  - Charge le noyau en mémoire à l'adresse `0x1000`.
  - Passe en mode protégé via `lgdt` et `ljmp`.
- **kernel.c** :
  - Initialise le mode texte VGA (`0xB8000`).
  - Boucle principale (affichage d'un message).
- **linker.ld** :
  - Définit les adresses de chargement (`0x1000` pour le noyau).

---

## **5. Comment Contribuer**
### **5.1. Règles de codage**
- **Assembleur** :
  - Commentaires **obligatoires** pour chaque section.
  - Labels en `snake_case` (ex: `enable_a20`).
- **C** :
  - Norme **C99**, pas de dépendances externes.
  - Fonctions préfixées par leur module (ex: `vga_putchar`).
- **Commits** :
  - Messages clairs en anglais (ex: `"feat(vga): Add color support"`).

### **5.2. Processus de contribution**
1. **Fork** le dépôt et créez une branche :
   ```bash
   git checkout -b feat/ma-fonctionnalite
   ```
2. **Testez** localement (QEMU + GDB).
3. **Soumettez une PR** avec :
   - Une description détaillée.
   - Des captures d'écran si UI/modifications visibles.
4. **Revue de code** :
   - Vérification du respect des règles.
   - Tests sur matériel réel (si possible).

### **5.3. Tâches prioritaires**
| Niveau       | Tâche                                  | Fichiers concernés          |
|--------------|----------------------------------------|-----------------------------|
| **Critique** | Gestion des interruptions (IDT)        | `kernel/interrupts.c`      |
| **Haut**     | Allocateur mémoire (heap)              | `kernel/memory/`           |
| **Moyen**    | Support clavier (IRQ1)                 | `kernel/drivers/keyboard.c`|
| **Bas**      | Amélioration de l'API VGA (couleurs)   | `kernel/vga.c`              |

---
## **6. Roadmap**
### **6.1. Version 0.2 (Q1 2025)**
- [ ] **Multitâche coopératif** (scheduler basique).
- [ ] **Système de fichiers FAT12** (lecture seule).
- [ ] **Pilotes** : Clavier, timer (PIT).
- [ ] **Debug** : Logs série + assertions.

### **6.2. Version 0.3 (Q2 2025)**
- [ ] **Mode graphique VESA** (résolution 1024x768).
- [ ] **Gestion mémoire paginée**.
- [ ] **Shell minimaliste** (commandes `ls`, `cat`).

### **6.3. Objectifs long terme**
- Support **UEFI** (remplacement du BIOS).
- Réseau (pilote **RTL8139**).
- Compatibilité **Raspberry Pi** (ARM).

---
## **7. Ressources Utiles**
- **Documentation x86** :
  - [Intel Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
  - [OSDev Wiki](https://wiki.osdev.org/)
- **Outils** :
  - [QEMU Monitor Commands](https://qemu-project.gitlab.io/qemu/system/monitor.html)
  - [GDB Cheatsheet](https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf)
- **Communauté** :
  - Canal Discord : `#maxos-dev` (lien à ajouter).

---
## **8. Licence**
MaxOS est distribué sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

---
*Documentation générée le 2024-10-01. Dernière mise à jour : [Git Commit

---
*MaxOS AI v18.0*
