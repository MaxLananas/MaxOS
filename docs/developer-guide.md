# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

```markdown
# **MaxOS – Documentation Technique (Prototype Bare Metal)**
*Version: 0.1-alpha | Statut: Boot x86 + VGA Texte 80x25*
*Dernière mise à jour: [DATE]*

---

## **1. Introduction**
MaxOS est un système d'exploitation **bare metal** en développement pour l'architecture **x86 (32-bit)**. Ce prototype implémente :
- **Boot minimal** (via GRUB/Multiboot)
- **Affichage texte VGA** (80x25, 16 couleurs)
- **Gestion basique du clavier** (PS/2)
- **Structure modulaire** (C + ASM)

**Technologies utilisées** :
- **Langages** : C (norme C99), Assembleur NASM (x86)
- **Outils** : GCC (cross-compilation), QEMU (émulation), Makefile
- **Cible** : Machines x86 (testé sur QEMU et matériel réel via USB bootable).

---

## **2. Prérequis**
### **2.1. Environnement de développement**
| Outil          | Version       | Installation (Linux/WSL)               |
|----------------|---------------|----------------------------------------|
| GCC (i686-elf) | ≥ 12.2        | `sudo apt install gcc-i686-elf-binutils`|
| NASM           | ≥ 2.15        | `sudo apt install nasm`                |
| QEMU           | ≥ 7.0         | `sudo apt install qemu-system-x86`     |
| Make           | ≥ 4.3         | `sudo apt install make`                |
| Git            | ≥ 2.30        | `sudo apt install git`                 |

### **2.2. Récupération du code**
```bash
git clone https://github.com/[votre-repo]/MaxOS.git
cd MaxOS
```

---

## **3. Compilation**
### **3.1. Structure des fichiers**
```
MaxOS/
├── src/
│   ├── kernel/          # Noyau principal (C)
│   │   ├── boot/        # Code de boot (ASM + C)
│   │   ├── drivers/     # Pilotes (VGA, clavier, etc.)
│   │   ├── memory/      # Gestion mémoire (à venir)
│   │   └── main.c      # Point d'entrée du noyau
│   ├── lib/             # Bibliothèques utilitaires
│   └── include/         # Headers partagés
├── tools/               # Scripts utilitaires
├── Makefile            # Règles de compilation
└── README.md           # Documentation utilisateur
```

### **3.2. Commandes de compilation**
#### **Compilation complète**
```bash
make all
```
- Génère `MaxOS.iso` (image bootable) dans `/build/`.

#### **Nettoyage**
```bash
make clean
```
- Supprime les fichiers objets et binaires.

#### **Détails du Makefile**
- **Cross-compilation** : Utilise `i686-elf-gcc` pour cibler x86 32-bit.
- **Liaison** : Crée un binaire ELF, converti en format **Multiboot** via `objcopy`.
- **Image ISO** : Combine le noyau avec GRUB via `grub-mkrescue`.

---

## **4. Test avec QEMU**
### **4.1. Lancement basique**
```bash
make run
```
- Équivalent à :
  ```bash
  qemu-system-x86_64 -cdrom build/MaxOS.iso -serial stdio -no-reboot
  ```
- **Options utiles** :
  - `-d int` : Afficher les interruptions CPU (debug).
  - `-s -S` : Attendre un débogueur (GDB) au démarrage.

### **4.2. Débogage avec GDB**
1. Lancez QEMU en mode debug :
   ```bash
   make debug
   ```
2. Dans une autre console, attachez GDB :
   ```bash
   i686-elf-gdb build/kernel.elf
   (gdb) target remote localhost:1234
   (gdb) continue
   ```

### **4.3. Sortie attendue**
- Écran VGA : Affichage du message `"MaxOS v0.1 – Boot successful"` en haut à gauche.
- **Problèmes courants** :
  - **Triple Fault** : Vérifiez les segments GDT/IDT (fichiers `boot/gdt.asm` et `boot/idt.c`).
  - **Écran noir** : Problème de liaison avec GRUB (vérifiez `grub.cfg`).

---

## **5. Structure du Code**
### **5.1. Point d'entrée (`boot/boot.asm`)**
- **Rôle** : Initialise les registres, charge le GDT, et saute en mode protégé.
- **Dépendances** :
  - `multiboot.h` (headers Multiboot pour GRUB).
  - `gdt.asm` (Global Descriptor Table).

### **5.2. Noyau (`kernel/main.c`)**
- **Fonctions clés** :
  - `kernel_main()` : Point d'entrée après le boot.
  - `terminal_init()` : Initialise le buffer VGA (adresse `0xB8000`).
  - `keyboard_init()` : Configure le contrôleur PS/2 (IRQ 1).

### **5.3. Pilotes**
| Fichier               | Responsabilité                          |
|-----------------------|-----------------------------------------|
| `drivers/vga.c`       | Gestion de l'affichage texte (couleurs, curseur). |
| `drivers/keyboard.c`  | Lecture des scans codes (US QWERTY).   |
| `drivers/serial.c`    | Port série (debug via `COM1`).          |

### **5.4. Conventions de code**
- **C** :
  - Norme **C99** (pas de C++).
  - Noms de fonctions en `snake_case`.
  - Headers protégés par `#pragma once`.
- **ASM** :
  - Commentaires NASM (`;`).
  - Labels en `UPPER_CASE`.

---

## **6. Contribuer au Projet**
### **6.1. Rapporter un bug**
- Utilisez les **GitHub Issues** avec le template :
  ```markdown
  **Description** : [Décrivez le problème]
  **Étapes pour reproduire** : [Commandes/exécutions]
  **Sortie attendue** : [Comportement normal]
  **Sortie obtenue** : [Erreur/plantage]
  **Environnement** : QEMU [version] / Matériel [détails]
  ```

### **6.2. Soumettre une Pull Request**
1. Forkez le dépôt.
2. Créez une branche :
   ```bash
   git checkout -b feature/[nom]
   ```
3. Respectez les conventions (voir §5.4).
4. Testez localement (`make run`).
5. Soumettez la PR avec une description claire des changements.

### **6.3. Tâches prioritaires**
| Domaine          | Tâche                                  | Difficulté |
|------------------|----------------------------------------|------------|
| **Mémoire**      | Implémenter un allocateur physique    | Moyenne    |
| **Pilotes**      | Support du clavier AZERTY               | Facile     |
| **Processus**    | Gestion basique des tâches (coopératif)| Difficile  |
| **FS**           | Lire un fichier depuis une image ISO   | Moyenne    |

---
## **7. Roadmap**
| Version  | Features                                                                 | Date cible   |
|----------|--------------------------------------------------------------------------|--------------|
| **0.1**  | Boot + VGA Texte (actuel)                                               | [Date]       |
| **0.2**  | Gestion mémoire physique + Allocateur heap                             | Q1 2025      |
| **0.3**  | Multitâche coopératif + Syscalls basiques                               | Q2 2025      |
| **0.4**  | Pilotes ATA (lecture disque) + Système de fichiers simple (FAT16)      | Q3 2025      |
| **1.0**  | Mode utilisateur + API stable                                          | 2026         |

---
## **8. Licence et Crédits**
- **Licence** : [MIT/GPLv3] (à préciser dans `LICENSE`).
- **Auteurs** :
  - [Votre Nom] (Mainteneur)
  - Contributeurs : [Liste GitHub].
-

---
*MaxOS AI v18.0*
