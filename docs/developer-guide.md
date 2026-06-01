# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée de manière professionnelle et détaillée.

---

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste en développement*

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental écrit en **C** et **ASM x86**, conçu pour apprendre les concepts fondamentaux des OS (bootloader, gestion mémoire, interruptions, etc.). Ce guide couvre la compilation, le test, l'architecture du projet, les contributions et la roadmap.

---

## **🔧 Prérequis**
- **Compilateur** : `gcc` (version 11+ recommandée)
- **Assembleur** : `nasm`
- **Émulateur** : `QEMU` (version 7+)
- **Outils** : `make`, `ld` (GNU Linker)
- **Bibliothèques** : Aucune dépendance externe (sauf pour le développement avancé).

---

## **📂 Structure des Fichiers**
MaxOS suit une architecture modulaire avec les dossiers principaux :

```bash
MaxOS/
├── boot/               # Bootloader et code ASM
│   ├── boot.asm        # Point d'entrée du bootloader
│   ├── gdt.asm         # Table des descripteurs globaux (GDT)
│   ├── idt.asm         # Table des interruptions (IDT)
│   ├── isr.asm         # Gestionnaires d'exceptions (ISR)
│   └── irq.asm         # Gestionnaires d'interruptions matérielles (IRQ)
│
├── kernel/             # Code noyau en C
│   ├── drivers/        # Pilotes (clavier, timer, etc.)
│   │   ├── keyboard.c  # Gestion du clavier PS/2
│   │   ├── timer.c     # Programmable Interval Timer (PIT)
│   │   └── ...
│   ├── core/           # Fonctions centrales
│   │   ├── fault_handler.c  # Gestion des exceptions
│   │   ├── paging.c    # Pagination mémoire
│   │   ├── heap.c      # Allocateur dynamique
│   │   └── ...
│   └── main.c          # Point d'entrée du noyau
│
├── include/            # En-têtes C
│   ├── system.h        # Définitions système
│   ├── isr.h           # Prototypes ISR/IRQ
│   └── ...
│
├── Makefile            # Script de compilation
└── README.md           # Documentation de base
```

### **📌 Fichiers Clés**
| Fichier          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `boot.asm`       | Charge le noyau en mémoire et initialise le mode protégé.                  |
| `gdt.asm`        | Définit la **Global Descriptor Table** (segments mémoire).                  |
| `idt.asm`        | Initialise la **Interrupt Descriptor Table** (vecteurs d'interruptions).    |
| `isr.asm`        | Gère les **exceptions CPU** (division par zéro, page fault, etc.).         |
| `irq.asm`        | Configure les **interruptions matérielles** (clavier, timer).              |
| `fault_handler.c`| Implémente la logique de gestion des exceptions.                           |
| `paging.c`       | Gère la **pagination** (mapping mémoire physique/virtuelle).                |
| `heap.c`         | Fournit un **allocateur dynamique** (kmalloc/kfree).                       |
| `keyboard.c`     | Pilote le **clavier PS/2** et interprète les scancodes.                    |
| `timer.c`        | Configure le **PIT** pour des interruptions périodiques (scheduling).       |

---

## **⚙️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation.

### **📌 Étapes**
1. **Nettoyer les anciens fichiers** (optionnel) :
   ```bash
   make clean
   ```
2. **Compiler le noyau** :
   ```bash
   make
   ```
   - **Sortie** : `kernel.bin` (image binaire du noyau).

### **🔍 Détails de la Compilation**
- **ASM** : Assemblé avec `nasm` (`-f elf32` pour le format 32 bits).
- **C** : Compilé avec `gcc` (`-m32 -ffreestanding -nostdlib` pour éviter les dépendances système).
- **Linker** : `ld` combine les objets en un binaire exécutable.

### **⚠️ Problèmes Courants**
- **Erreur de 32 bits** : Installer les bibliothèques `gcc-multilib` et `libc6-dev-i386`.
- **Linker** : Vérifier que `ld` est configuré pour l'architecture `i386`.

---

## **🧪 Test avec QEMU**
MaxOS est conçu pour être testé dans **QEMU**.

### **📌 Commande de Base**
```bash
make run
```
- **Options QEMU** :
  - `-kernel kernel.bin` : Charge le noyau.
  - `-m 128M` : Alloue 128 Mo de RAM.
  - `-serial stdio` : Affiche la sortie série dans le terminal.

### **🔧 Débogage Avancé**
1. **Déboguer avec GDB** :
   ```bash
   qemu-system-i386 -kernel kernel.bin -s -S &
   gdb -ex "target remote localhost:1234" -ex "symbol-file kernel.elf"
   ```
2. **Logs QEMU** :
   ```bash
   qemu-system-i386 -kernel kernel.bin -d int,cpu_reset
   ```

---

## **🤝 Contribuer**
MaxOS est un projet **open-source** et accueille les contributions !

### **📌 Comment Contribuer**
1. **Forker le dépôt** sur GitHub/GitLab.
2. **Créer une branche** :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
3. **Implémenter la fonctionnalité** :
   - Respecter le style de code (indentation, noms de variables).
   - Documenter le code avec des commentaires.
4. **Soumettre une Pull Request** avec une description claire.

### **📌 Bonnes Pratiques**
- **Tests** : Toujours tester les modifications dans QEMU.
- **Style** : Utiliser `clang-format` pour uniformiser le code.
- **Issues** : Signaler les bugs ou proposer des features via GitHub Issues.

### **📌 Exemples de Contributions**
- Ajouter un **pilote** (ex: souris PS/2).
- Implémenter un **système de fichiers** (FAT16).
- Optimiser la **gestion mémoire** (slab allocator).
- Corriger des **bugs** (ex: exceptions non gérées).

---

## **🗺️ Roadmap**
Voici les **objectifs à court/moyen terme** pour MaxOS :

### **📌 Phase 1 : Stabilisation (Mois 1-3)**
- [ ] **Gestion avancée des exceptions** (triple fault, NMI).
- [ ] **Scheduling basique** (round-robin).
- [ ] **Support des appels système** (syscalls).
- [ ] **Gestion des périphériques** (VGA, disque dur).

### **📌 Phase 2 : Fonctionnalités (Mois 4-6)**
- [ ] **Système de fichiers** (FAT32).
- [ ] **Multitâche préemptif** (avec priorités).
- [ ] **Réseau basique** (TCP/IP via NE2000).
- [ ] **Shell intégré** (interpréteur de commandes).

### **📌 Phase 3 : Optimisation (Mois 7+)**
- [ ] **Optimisation mémoire** (buddy allocator).
- [ ] **Support SMP** (multi-cœurs).
- [ ] **Sécurité** (ASLR, protection mémoire).
- [ ] **Portabilité** (support x86_64).

### **📌 Idées Long Terme**
- **Port vers ARM/RISC-V**.
- **Compatibilité avec Linux** (via un module noyau).
- **Interface graphique** (framebuffer).

---

## **📜 Licence**
MaxOS est distribué sous la **licence MIT** (voir `LICENSE`).

---

## **📞 Contact & Ressources**
- **GitHub** : [https://github.com/maxos-dev/maxos](https://github.com/maxos-dev/maxos)
- **Documentation** : [

---
*MaxOS AI v18.0*
