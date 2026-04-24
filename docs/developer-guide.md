# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée de manière professionnelle et couvrant tous les aspects demandés :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*

**Niveau** : Prototype bare metal
**Score** : 35/100
**Fichiers** : 46 (C) | 14 (ASM)

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental conçu pour :
- Démarrer sur architecture x86 (32 bits).
- Afficher un terminal texte en mode VGA 80x25.
- Servir de base pour l'apprentissage des concepts OS (interruptions, gestion mémoire, etc.).

Ce guide détaille les aspects techniques pour les développeurs souhaitant contribuer ou étendre le projet.

---

## **🔧 1. Compilation**
### **Prérequis**
- **Compilateur** : `gcc` (version 9+) ou `clang` avec support cross-compilation.
- **Assembleur** : `nasm` (pour les fichiers `.asm`).
- **Outils** : `make`, `ld` (GNU Linker), `qemu-system-x86` (pour le test).
- **Bibliothèques** : Aucune dépendance externe (sauf pour QEMU).

### **Étapes de compilation**
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

2. **Compiler le noyau** :
   ```bash
   make
   ```
   - Le Makefile génère :
     - `kernel.bin` (noyau binaire).
     - `kernel.elf` (version symbolique pour le débogage).

3. **Options avancées** :
   - **Debug** : `make debug` (active les symboles de débogage).
   - **Optimisation** : `make OPTIMIZE=1` (active `-O2`).

> ⚠️ **Note** : Le noyau est compilé en **mode 32 bits** (`-m32`). Assurez-vous que votre toolchain supporte cela.

---

## **🧪 2. Test avec QEMU**
### **Lancement de base**
```bash
make run
```
- QEMU démarre avec :
  - 128 Mo de RAM.
  - Affichage en mode texte VGA 80x25.
  - Port série redirigé vers `stdio`.

### **Options personnalisées**
| Commande | Description |
|----------|-------------|
| `make run-debug` | Lance QEMU avec le débogueur intégré (`-s -S`). |
| `make run-serial` | Redirige la sortie vers un fichier (`serial.log`). |
| `make run-gdb` | Connecte GDB au noyau (nécessite `gdb` avec support i386). |

### **Débogage avec GDB**
1. Dans un terminal, lancez :
   ```bash
   make run-debug
   ```
2. Dans un second terminal :
   ```bash
   gdb kernel.elf
   (gdb) target remote localhost:1234
   (gdb) continue
   ```

> 🔍 **Astuce** : Utilisez `Ctrl+A C` dans QEMU pour basculer vers la console.

---

## **📂 3. Structure des Fichiers**
```
maxos/
├── **boot/**          # Code de démarrage (ASM)
│   ├── boot.asm       # Chargeur de démarrage (MBR)
│   └── loader.asm     # Charge le noyau en mémoire
├── **kernel/**        # Noyau principal (C)
│   ├── main.c         # Point d'entrée du noyau
│   ├── drivers/       # Pilotes (VGA, clavier, etc.)
│   ├── fs/            # Système de fichiers (basique)
│   ├── mm/            # Gestion mémoire (PMM, heap)
│   └── arch/x86/      # Code spécifique à l'architecture
├── **lib/**           # Bibliothèques utilitaires
│   ├── stdio.c        # Gestion de l'affichage
│   ├── string.c       # Fonctions de chaîne
│   └── ...
├── **include/**       # En-têtes
├── **Makefile**       # Script de compilation
├── **linker.ld**      # Script de linkage
└── **docs/**          # Documentation
```

### **Fichiers clés**
| Fichier | Rôle |
|---------|------|
| `boot/boot.asm` | Charge le secteur de boot en mémoire (512 octets). |
| `kernel/main.c` | Point d'entrée du noyau (`kernel_main()`). |
| `kernel/drivers/vga.c` | Gestion de l'affichage texte (80x25). |
| `kernel/mm/pmm.c` | Allocateur de mémoire physique (bitmap). |
| `linker.ld` | Définit l'adressage mémoire du noyau (0x100000). |

---

## **🤝 4. Contribuer**
MaxOS est un projet open-source. Voici comment contribuer :

### **1. Forker le dépôt**
- Créez une branche dédiée :
  ```bash
  git checkout -b feature/ma-nouvelle-fonctionnalite
  ```

### **2. Ajouter une fonctionnalité**
- **Nouveau pilote** : Placez-le dans `kernel/drivers/`.
- **Nouveau système** : Créez un sous-dossier dédié (ex: `fs/`).
- **Correction de bug** : Ajoutez des tests dans `tests/`.

### **3. Soumettre une Pull Request**
1. Poussez votre branche :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
2. Ouvrez une PR sur GitHub avec :
   - Une description claire.
   - Des tests unitaires (si applicable).
   - Une documentation mise à jour.

### **📌 Bonnes pratiques**
- **Style de code** : Respectez le style existant (indentation, noms de variables).
- **Commentaires** : Documentez les fonctions critiques.
- **Tests** : Ajoutez des tests dans `tests/` (ex: `tests/vga_test.c`).

---

## **🗺️ 5. Roadmap**
Voici les objectifs à court et moyen terme pour MaxOS :

### **🔹 Phase 1 : Stabilisation (Courant)**
- [x] Boot fonctionnel (x86, VGA 80x25).
- [x] Gestion basique de la mémoire (PMM).
- [ ] **Priorité** : Ajout d'un système de fichiers (FAT16).
- [ ] **Priorité** : Gestion des interruptions (IDT).

### **🔹 Phase 2 : Fonctionnalités avancées (6-12 mois)**
- [ ] Multitâche préemptif (scheduler simple).
- [ ] Gestion des processus (fork/exec).
- [ ] Pilotes pour clavier et disque (ATA PIO).
- [ ] Support du mode protégé (32 bits).

### **🔹 Phase 3 : Extensions (12+ mois)**
- [ ] Support du mode long (64 bits).
- [ ] Réseau basique (TCP/IP).
- [ ] Interface utilisateur graphique (VESA).
- [ ] Compatibilité avec des applications utilisateur (ELF).

### **🔹 Idées à long terme**
- Portage sur ARM (Raspberry Pi).
- Système de paquets (comme `apt`).
- Support des périphériques USB.

---

## **📚 Ressources Utiles**
- **Références** :
  - [OSDev Wiki](https://wiki.osdev.org/) (indispensable).
  - *Operating Systems: Three Easy Pieces* (livre gratuit).
  - *Linux Kernel Development* (Robert Love).
- **Outils** :
  - `qemu-system-x86_64` (émulation).
  - `bochs` (débogage avancé).
  - `gdb` (débogage du noyau).

---

## **📜 Licence**
MaxOS est distribué sous la licence **MIT** (voir `LICENSE`).

---

## **💬 Contact**
Pour des questions ou suggestions :
- **Email** : contact@maxos.dev
- **Discord** : [Lien vers le serveur Discord]
- **Issues** : [GitHub Issues](https://github.com/votre-utilisateur/maxos/issues)

---
*Documentation générée le `date`. Dernière mise à jour : v0.1-alpha.*
```

---

### **

---
*MaxOS AI v18.0*
