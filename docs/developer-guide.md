# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage texte VGA 80x25
- **Fichiers** : 57 en C, 19 en ASM

---

## **📌 Table des Matières**
1. [Prérequis](#prérequis)
2. [Compilation](#compilation)
3. [Test avec QEMU](#test-avec-qemu)
4. [Structure des Fichiers](#structure-des-fichiers)
5. [Contribuer](#contribuer)
6. [Roadmap](#roadmap)
7. [Licence](#licence)

---

## **🔧 Prérequis**
Pour compiler et tester MaxOS, vous aurez besoin de :
- **Compilateur** : `gcc` (version ≥ 11) ou `clang`
- **Assembleur** : `nasm` (pour les fichiers `.asm`)
- **Linker** : `ld` (GNU Linker)
- **Émulateur** : `qemu-system-x86_64` (pour les tests)
- **Outils** : `make` (pour automatiser la compilation)
- **Bibliothèques** : Aucune dépendance externe (sauf `libc` minimale si utilisée)

> **Note** : MaxOS est conçu pour un environnement bare metal. Aucune dépendance système n'est requise.

---

## **🏗️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation. Voici les étapes :

### **1. Cloner le dépôt**
```bash
git clone https://github.com/votre-utilisateur/maxos.git
cd maxos
```

### **2. Compiler le noyau**
```bash
make clean   # Nettoie les fichiers temporaires
make         # Compile le noyau et génère `maxos.bin`
```

### **3. Fichiers générés**
- `maxos.bin` : Image binaire du noyau (format ELF ou raw selon la configuration).
- `maxos.iso` : Image ISO bootable (optionnelle, si supporté).

> **Options de compilation** :
> - `make DEBUG=1` : Active les logs de débogage.
> - `make VGA=1` : Force le mode VGA 80x25 (par défaut).

---

## **🧪 Test avec QEMU**
MaxOS est testé avec **QEMU**, un émulateur x86. Voici comment lancer le système :

### **1. Lancer QEMU**
```bash
make run   # Utilise `qemu-system-x86_64` avec les paramètres par défaut
```
**Paramètres par défaut** :
- CPU : `qemu32` (compatibilité maximale)
- RAM : `128M`
- Affichage : `std-vga` (mode texte 80x25)
- Disque : Aucun (boot direct depuis l'image binaire)

### **2. Options avancées**
```bash
qemu-system-x86_64 -kernel maxos.bin -m 256 -vga std -serial stdio
```
- `-kernel` : Charge l'image binaire directement.
- `-m` : Définit la RAM (ex: `256` pour 256 Mo).
- `-vga std` : Force le mode VGA standard.
- `-serial stdio` : Redirige la sortie série vers le terminal.

### **3. Débogage avec GDB**
Pour déboguer le noyau :
```bash
make debug   # Lance QEMU avec GDB attaché
```
Puis dans un autre terminal :
```bash
gdb -q maxos.bin
(gdb) target remote localhost:1234
(gdb) continue
```

---

## **📂 Structure des Fichiers**
MaxOS suit une architecture **modulaire** avec les dossiers principaux suivants :

```
maxos/
├── **boot/**          # Code de démarrage (ASM)
│   ├── boot.asm       # Point d'entrée (MBR)
│   ├── gdt.asm        # Table des descripteurs globaux
│   └── idt.asm        # Table des interruptions
│
├── **kernel/**        # Noyau principal (C)
│   ├── main.c         # Fonction principale
│   ├── drivers/       # Pilotes (VGA, clavier, etc.)
│   ├── memory/        # Gestion mémoire
│   └── sys/           # Appels système
│
├── **lib/**           # Bibliothèques utilitaires
│   ├── stdio.c        # Gestion de l'affichage
│   ├── string.c       # Fonctions de chaîne
│   └── util.h         # Macros et constantes
│
├── **include/**       # En-têtes
│   ├── kernel.h       # Définitions du noyau
│   └── arch/x86/      # Dépendances x86
│
├── **Makefile**       # Règles de compilation
├── **linker.ld**      # Script de liaison (linker)
└── **README.md**      # Documentation
```

### **Détails clés**
- **`boot/`** : Code en **ASM** pour initialiser le CPU (mode réel → protégé).
- **`kernel/`** : Logique principale en **C**, avec séparation des responsabilités.
- **`lib/`** : Fonctions réutilisables (ex: `printf` pour VGA).
- **`linker.ld`** : Définit l'adressage mémoire (ex: `0x100000` pour le noyau).

---

## **🤝 Contribuer**
MaxOS est un projet **open-source** et accueille les contributions. Voici comment participer :

### **1. Forker le dépôt**
1. Créez un fork sur [GitHub](https://github.com/votre-utilisateur/maxos/fork).
2. Clonez votre fork :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

### **2. Créer une branche**
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### **3. Implémenter votre contribution**
- **Nouveau pilote** : Ajoutez dans `kernel/drivers/`.
- **Fonctionnalité système** : Modifiez `kernel/main.c` ou `sys/`.
- **Optimisation** : Proposez des améliorations dans `lib/`.

### **4. Tester**
```bash
make clean && make
make run
```

### **5. Soumettre une Pull Request (PR)**
1. Poussez vos changements :
   ```bash
   git add .
   git commit -m "Ajout du support du clavier PS/2"
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
2. Ouvrez une PR sur le dépôt principal avec une description claire.

### **📌 Bonnes pratiques**
- **Code** : Respectez le style (indentation, noms de variables).
- **Documentation** : Ajoutez des commentaires pour les fonctions complexes.
- **Tests** : Vérifiez que votre code compile et fonctionne avec `make run`.

---

## **🗺️ Roadmap**
MaxOS est en phase de **prototype**. Voici les étapes prévues :

| **Phase**       | **Objectif**                          | **Statut**       |
|------------------|---------------------------------------|------------------|
| **Bootloader**   | Chargement du noyau en mémoire        | ✅ Terminé       |
| **VGA Text**     | Affichage 80x25                      | ✅ Terminé       |
| **GDT/IDT**      | Gestion des interruptions             | ✅ Terminé       |
| **Clavier**      | Pilote PS/2 basique                  | 🔄 En cours      |
| **Mémoire**      | Allocation dynamique                  | 🚧 À faire       |
| **Système de fichiers** | Support FAT16/32              | 🚧 À faire       |
| **Multitâche**   | Ordonnanceur basique                  | 🚧 À faire       |
| **Réseau**       | Pilote Ethernet (ex: RTL8139)         | 🚧 À faire       |

### **🔮 Futures fonctionnalités**
- **ACPI** : Gestion de l'énergie.
- **APIC** : Interruptions avancées.
- **Modules** : Chargement dynamique de pilotes.
- **GUI** : Mode graphique (VESA).

---

## **📜 Licence**
MaxOS

---
*MaxOS AI v18.0*
