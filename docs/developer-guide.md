# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

```markdown
# **Documentation Technique MaxOS**
*Un système d'exploitation minimaliste pour x86 en mode texte*

**Score** : 35/100 (Prototype bare metal)
**Fichiers** : 42 en C, 13 en ASM
**Cible** : x86 (émulé via QEMU ou exécuté sur matériel)
**Mode** : VGA texte 80x25

---

## **📌 Introduction**
MaxOS est un système d'exploitation minimaliste conçu pour apprendre les bases du développement bare metal. Il inclut un bootloader, un noyau en C/ASM, et des pilotes basiques pour l'affichage VGA. Ce guide couvre la compilation, le test, la structure du projet, et les contributions.

---

## **🔧 1. Compilation du Projet**

### **📦 Prérequis**
- **Compilateur** : `gcc` (version croisée pour x86) ou `i686-elf-gcc` (recommandé).
- **Assembleur** : `nasm` ou `as`.
- **Outils** : `ld` (linker), `objcopy` (pour générer l'image disque).
- **Émulateur** : QEMU (pour le test).
- **Système** : Linux (recommandé) ou WSL.

### **🛠️ Étapes de compilation**
1. **Installer les dépendances** (exemple sous Debian/Ubuntu) :
   ```bash
   sudo apt install build-essential nasm qemu-system-x86 grub2 xorriso
   ```

2. **Compiler le noyau et le bootloader** :
   ```bash
   make clean && make
   ```
   - Le script `Makefile` génère :
     - `boot.bin` : Bootloader (secteur de boot + noyau).
     - `kernel.bin` : Noyau en ELF.
     - `maxos.iso` : Image disque bootable (format ISO).

3. **Vérifier les binaires** :
   ```bash
   file kernel.bin boot.bin maxos.iso
   ```
   - `kernel.bin` doit être un binaire ELF 32 bits.
   - `maxos.iso` doit être une image ISO valide.

---

## **🧪 2. Test avec QEMU**

### **🚀 Lancer MaxOS dans QEMU**
```bash
qemu-system-x86_64 -cdrom maxos.iso -m 128M -vga std
```
- **Options** :
  - `-cdrom maxos.iso` : Charge l'image ISO.
  - `-m 128M` : Alloue 128 Mo de RAM (ajustable).
  - `-vga std` : Force le mode VGA standard (80x25).

### **🐞 Débogage**
- **Afficher les logs** :
  ```bash
  qemu-system-x86_64 -cdrom maxos.iso -serial stdio
  ```
  - Les messages du noyau s'affichent dans le terminal.
- **Debugger avec GDB** :
  ```bash
  qemu-system-x86_64 -cdrom maxos.iso -s -S &
  gdb -ex "target remote localhost:1234" -ex "symbol-file kernel.bin"
  ```

### **💡 Astuces**
- Pour un redémarrage rapide, utilisez :
  ```bash
  make run
  ```
  (si le `Makefile` est configuré pour cela).

---

## **📂 3. Structure des Fichiers**

```
maxos/
├── boot/               # Bootloader et secteur de boot
│   ├── boot.asm        # Code assembleur du bootloader
│   └── boot_sect.bin   # Secteur de boot (512 octets)
├── kernel/             # Noyau et pilotes
│   ├── kernel.c        # Point d'entrée du noyau
│   ├── drivers/        # Pilotes matériels
│   │   ├── vga.c       # Gestion de l'affichage VGA
│   │   └── keyboard.c  # Pilote clavier (PS/2)
│   ├── lib/            # Bibliothèques utilitaires
│   │   ├── string.c    # Fonctions de chaîne
│   │   └── stdio.c     # Entrée/sortie basique
│   └── Makefile        # Compilation du noyau
├── tools/              # Outils de build
│   ├── linker.ld       # Script de linkage
│   └── mkiso.sh        # Génération de l'ISO
├── include/            # En-têtes
│   ├── kernel.h        # Définitions du noyau
│   └── drivers/        # En-têtes des pilotes
├── docs/               # Documentation
└── Makefile            # Compilation globale
```

### **📌 Détails clés**
- **Bootloader** :
  - `boot.asm` charge le noyau depuis le disque (secteur 2) en mémoire.
  - Le secteur de boot (`boot_sect.bin`) est généré avec `nasm`.
- **Noyau** :
  - `kernel.c` initialise le matériel et lance les pilotes.
  - Les pilotes (`vga.c`, `keyboard.c`) interagissent avec le matériel via des ports E/S.
- **Linker Script** (`linker.ld`) :
  - Définit l'adresse de chargement du noyau (ex: `0x1000`).
  - Spécifie les sections `.text`, `.data`, `.bss`.

---

## **🤝 4. Contribuer au Projet**

MaxOS est open-source et accepte les contributions ! Voici comment participer :

### **📌 Étapes pour contribuer**
1. **Forker le dépôt** sur GitHub/GitLab.
2. **Créer une branche** :
   ```bash
   git checkout -b feature/ma-nouvelle-fonction
   ```
3. **Implémenter votre changement** :
   - Ajoutez des pilotes (ex: disque dur, réseau).
   - Optimisez le code existant.
   - Corrigez des bugs (voir les [issues](https://github.com/votre-repo/maxos/issues)).
4. **Tester** :
   - Vérifiez que le projet compile (`make`).
   - Testez dans QEMU (`make run`).
5. **Soumettre une Pull Request** :
   - Décrivez clairement les changements.
   - Incluez des tests si possible.

### **📜 Règles de contribution**
- **Style de code** :
  - Respectez le style existant (indentation, noms de variables).
  - Utilisez des commentaires pour les parties complexes.
- **Documentation** :
  - Mettez à jour le `README.md` si nécessaire.
  - Documentez les nouvelles fonctions dans les en-têtes.
- **Tests** :
  - Ajoutez des tests unitaires si possible (ex: pour `lib/string.c`).

### **🎯 Exemples de contributions**
- **Pilotes** : Ajouter un pilote pour le clavier USB.
- **Système de fichiers** : Implémenter un système FAT16.
- **Multitâche** : Ajouter un scheduler basique.
- **Optimisations** : Réduire la taille du binaire.

---

## **🗺️ 5. Roadmap**

| **Version** | **Fonctionnalités**                          | **Statut**       | **Date estimée** |
|-------------|---------------------------------------------|------------------|------------------|
| **0.1**     | Bootloader + VGA texte 80x25               | ✅ Terminé       | 2023-10          |
| **0.2**     | Pilote clavier PS/2                         | ✅ Terminé       | 2023-11          |
| **0.3**     | Gestion basique de la mémoire               | 🔄 En cours      | 2024-01          |
| **0.4**     | Système de fichiers (FAT16)                 | 🚧 Planifié      | 2024-03          |
| **0.5**     | Multitâche préemptif                       | 🚧 Planifié      | 2024-05          |
| **0.6**     | Pilote réseau (NE2000)                     | 🚧 Planifié      | 2024-07          |
| **1.0**     | Version stable avec documentation complète | 🚧 Long terme    | 2025-01          |

### **🔮 Objectifs à long terme**
- **Portabilité** : Support d'autres architectures (ARM, RISC-V).
- **

---
*MaxOS AI v18.0*
