# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée de manière professionnelle et détaillée :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste en développement*

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental écrit en **C** et **ASM x86**, conçu pour apprendre les bases des noyaux modernes. Il inclut un **bootloader**, une **GDT/IDT**, des **interruptions**, un **terminal basique** et une **gestion matérielle** (clavier, écran, timer).

Ce guide couvre la compilation, le test, l'architecture du projet, les contributions et la roadmap.

---

## **🔧 1. Compilation du Projet**

### **📦 Prérequis**
- **Compilateur** : `gcc` (pour le code C) et `nasm` (pour l'ASM).
- **Outils** : `make` (pour automatiser la compilation), `qemu-system-x86_64` (pour l'émulation).
- **Bibliothèques** : Aucune dépendance externe (sauf pour QEMU).

### **🛠️ Étapes de Compilation**
1. **Cloner le dépôt** (si applicable) :
   ```bash
   git clone https://github.com/votre-utilisateur/MaxOS.git
   cd MaxOS
   ```

2. **Compiler avec `make`** :
   ```bash
   make
   ```
   - **Fichiers générés** :
     - `kernel.bin` (noyau binaire).
     - `boot.bin` (bootloader).
     - `MaxOS.iso` (image ISO bootable).

3. **Nettoyer les fichiers temporaires** :
   ```bash
   make clean
   ```

> **Note** : Le `Makefile` est configuré pour :
> - Compiler les fichiers `.c` en `.o` avec `gcc`.
> - Assembler les fichiers `.asm` avec `nasm`.
> - Lier le tout en un binaire exécutable.

---

## **🧪 2. Test dans QEMU**

### **🚀 Lancer MaxOS dans QEMU**
```bash
make run
```
- **Options par défaut** :
  - `-kernel kernel.bin` : Charge le noyau en mémoire.
  - `-serial stdio` : Affiche la sortie série dans le terminal.
  - `-m 128M` : Alloue 128 Mo de RAM.

### **🔍 Débogage avec GDB**
Pour déboguer le noyau :
```bash
make debug
```
- **Fonctionnalités** :
  - Arrêt au point d'entrée (`_start`).
  - Inspection des registres et de la mémoire.
  - Suivi des interruptions.

### **📝 Exemple de Sortie Attendue**
```
MaxOS v0.1 - Terminal prêt
> help
Commandes disponibles : clear, reboot, poweroff
```

---

## **📂 3. Structure des Fichiers**

```
MaxOS/
├── boot/               # Bootloader et initialisation
│   ├── boot.asm        # Code ASM du bootloader (charge le noyau)
│   └── boot_sect.bin   # Secteur de boot (512 octets)
├── kernel/             # Noyau principal
│   ├── arch/           # Architecture x86
│   │   ├── gdt.asm     # Table des descripteurs globaux
│   │   ├── idt.asm     # Table des interruptions
│   │   ├── isr.asm     # Gestion des exceptions (ISR)
│   │   └── irq.asm     # Gestion des IRQ (clavier, timer)
│   ├── drivers/        # Pilotes matériels
│   │   ├── keyboard.c  # Gestion du clavier PS/2
│   │   ├── screen.c    # Affichage texte (VGA)
│   │   └── timer.c     # Timer PIT (Programmable Interval Timer)
│   ├── core/           # Fonctions centrales
│   │   ├── exceptions.c # Gestion des exceptions CPU
│   │   └── terminal.c  # Terminal basique (commandes)
│   └── Makefile        # Règles de compilation
├── tools/              # Outils utilitaires
│   └── link.ld         # Script de liaison (linker)
├── Makefile            # Compilation globale
└── README.md           # Documentation
```

### **📌 Description des Composants Clés**
| Fichier/Dossier | Rôle |
|-----------------|------|
| `boot.asm` | Charge le noyau en mémoire (mode 32 bits). |
| `gdt.asm` | Initialise la **Global Descriptor Table** (segments mémoire). |
| `idt.asm` | Configure la **Interrupt Descriptor Table** (vecteurs d'interruption). |
| `isr.asm` | Gère les **exceptions CPU** (division par zéro, page fault, etc.). |
| `irq.asm` | Gère les **interruptions matérielles** (clavier, timer). |
| `keyboard.c` | Lit les scancodes du clavier et les convertit en caractères. |
| `screen.c` | Affiche du texte en mode VGA (80x25). |
| `timer.c` | Initialise le **PIT** pour des interruptions périodiques. |
| `terminal.c` | Interface en ligne de commande (commandes `clear`, `help`). |

---

## **🤝 4. Contribuer au Projet**

### **📌 Comment Participer ?**
MaxOS est un projet **open-source** ! Voici comment contribuer :

1. **Forker le dépôt** sur GitHub.
2. **Créer une branche** pour votre feature :
   ```bash
   git checkout -b feature/nouvelle-commande
   ```
3. **Implémenter votre code** (respectez le style existant).
4. **Tester** avec `make run` et `make debug`.
5. **Soumettre une Pull Request** avec une description claire.

### **📜 Bonnes Pratiques**
- **Style de code** :
  - Utilisez **4 espaces** pour l'indentation.
  - Noms de variables/fonctions en **snake_case** (`void handle_keyboard()`).
  - Commentaires en **français** pour les fonctions critiques.
- **Documentation** :
  - Ajoutez des commentaires pour les fonctions complexes.
  - Mettez à jour ce `README.md` si nécessaire.
- **Tests** :
  - Vérifiez que votre code ne casse pas la compilation.
  - Testez dans QEMU avant de soumettre.

### **🔧 Exemple de Contribution**
- **Ajouter une commande `echo`** :
  1. Modifiez `terminal.c` :
     ```c
     void cmd_echo(char *args) {
         printf("> %s\n", args);
     }
     ```
  2. Ajoutez la commande dans `terminal.c` :
     ```c
     if (strcmp(cmd, "echo") == 0) cmd_echo(args);
     ```
  3. Testez avec `make run` et validez.

---

## **🗺️ 5. Roadmap du Projet**

### **📅 Objectifs à Court Terme (v0.2 - v0.5)**
| Version | Fonctionnalités | Statut |
|---------|-----------------|--------|
| **v0.2** | Gestion de la mémoire (heap basique) | ⏳ |
| **v0.3** | Système de fichiers (FAT16) | ⏳ |
| **v0.4** | Multitâche (scheduling basique) | ⏳ |
| **v0.5** | Support du clavier USB | ⏳ |

### **🚀 Objectifs à Moyen Terme (v1.0)**
- **Gestion avancée de la mémoire** (paging, malloc/free).
- **Pilotes** : Disque dur (ATA), carte réseau (pour TCP/IP).
- **Système de fichiers** : Ext2 ou propre format.
- **API système** : Appels système (`syscall`).

### **🌌 Objectifs à Long Terme (v2.0+)**
- **Portabilité** : Support x86_64 et ARM.
- **Graphismes** : Mode graphique (VESA).
- **Réseau** : Stack TCP/IP complète.
- **Compatibilité** : Exécuter des programmes ELF.

### **📌 Comment Suivre l'Avancement ?**
- Consultez les **issues GitHub** pour les tâches en cours.
- Rejoignez le **Discord** ou le **forum** du projet pour discuter des idées.

---

## **📜

---
*MaxOS AI v18.0*
