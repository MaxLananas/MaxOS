# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*

**Score** : 35/100 (Prototype bare metal)
**Fichiers** : 38 (C) | 8 (ASM)
**Dernière mise à jour** : [Date]

---

## **Table des matières**
1. [Prérequis](#prérequis)
2. [Compilation](#compilation)
3. [Test avec QEMU](#test-avec-qemu)
4. [Structure des fichiers](#structure-des-fichiers)
5. [Contribuer](#contribuer)
6. [Roadmap](#roadmap)
7. [Licence](#licence)

---

## **Prérequis**
Pour compiler et tester MaxOS, vous aurez besoin de :
- **Compilateur** : `gcc` (version ≥ 11) ou `clang`
- **Assembleur** : `nasm` (pour les fichiers `.asm`)
- **Émulateur** : `qemu-system-x86_64` (version ≥ 7.0)
- **Outils** : `make`, `ld` (GNU Linker), `objcopy`
- **Bibliothèques** : Aucune (système autonome)

> **Note** : Sous Linux, installez les dépendances via :
> ```bash
> sudo apt install build-essential nasm qemu-system-x86
> ```

---

## **Compilation**
MaxOS utilise un système de build basé sur `make`. Voici les étapes :

### **1. Cloner le dépôt**
```bash
git clone https://github.com/votre-utilisateur/maxos.git
cd maxos
```

### **2. Compiler le noyau**
Exécutez la commande suivante pour générer l'image disque `maxos.img` :
```bash
make
```
**Options disponibles** :
- `make clean` : Nettoie les fichiers temporaires.
- `make debug` : Active les logs de débogage (nécessite `DEBUG=1` dans le Makefile).
- `make run` : Compile et lance QEMU automatiquement.

### **3. Fichiers générés**
Après compilation, vous obtiendrez :
- `maxos.bin` : Image binaire du noyau (format ELF).
- `maxos.img` : Image disque bootable (format FAT16).
- `kernel.elf` : Fichier ELF du noyau (pour débogage avec `gdb`).

---

## **Test avec QEMU**
MaxOS est conçu pour être testé dans QEMU. Voici comment procéder :

### **1. Lancer QEMU**
```bash
make run
```
**Options avancées** :
- **Mode graphique** (VGA texte) :
  ```bash
  qemu-system-x86_64 -drive format=raw,file=maxos.img -vga std
  ```
- **Débogage avec GDB** :
  ```bash
  qemu-system-x86_64 -s -S -drive format=raw,file=maxos.img &
  gdb kernel.elf
  ```
  *(Dans GDB : `target remote localhost:1234` puis `continue`)*

### **2. Vérifier la sortie**
MaxOS affiche un message de bienvenue en mode texte 80x25 :
```
MaxOS v0.1 (Prototype)
Copyright (C) 2023 Votre Nom
```
Si le système plante, QEMU affichera un message d'erreur (ex : `Triple fault`).

---

## **Structure des fichiers**
Voici l'arborescence principale de MaxOS :

```plaintext
maxos/
├── boot/               # Code de boot (ASM)
│   ├── boot.asm        # Chargeur de démarrage (secteur 0)
│   └── gdt.asm         # Table des descripteurs globaux
├── kernel/             # Noyau (C)
│   ├── main.c          # Point d'entrée du noyau
│   ├── drivers/        # Pilotes matériels
│   │   ├── vga.c       # Gestion de l'affichage texte
│   │   └── keyboard.c  # Pilote clavier PS/2
│   ├── lib/            # Bibliothèques utilitaires
│   │   ├── string.c    # Fonctions de chaîne
│   │   └── stdio.c     # Entrées/sorties basiques
│   └── include/        # En-têtes
│       ├── kernel.h    # Définitions du noyau
│       └── drivers.h   # Prototypes des pilotes
├── tools/              # Outils de build
│   ├── linker.ld       # Script de liaison
│   └── Makefile        # Règles de compilation
├── disk/               # Contenu du disque
│   └── boot/           # Fichiers de boot
├── docs/               # Documentation
└── README.md           # Ce fichier
```

### **Fichiers clés**
| Fichier          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `boot.asm`       | Charge le noyau en mémoire (mode réel → mode protégé).                     |
| `main.c`         | Point d'entrée du noyau (initialisation matérielle, boucle principale).    |
| `vga.c`          | Gère l'affichage en mode texte (80x25) via les ports VGA.                  |
| `keyboard.c`     | Pilote le clavier PS/2 et gère les interruptions IRQ1.                     |
| `linker.ld`      | Définit la disposition mémoire du noyau (sections `.text`, `.data`, etc.). |

---

## **Contribuer**
MaxOS est un projet open source. Voici comment contribuer :

### **1. Forker le dépôt**
1. Créez un fork sur GitHub.
2. Clonez votre fork :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   ```

### **2. Créer une branche**
```bash
git checkout -b feature/nom-de-la-fonction
```

### **3. Implémenter une fonctionnalité**
- **Nouveau pilote** : Ajoutez un fichier dans `kernel/drivers/` et incluez-le dans `kernel/main.c`.
- **Amélioration du noyau** : Modifiez `kernel/main.c` ou les fichiers de la bibliothèque.
- **Correction de bug** : Ouvrez une issue avant de proposer une PR.

### **4. Tester vos modifications**
```bash
make clean && make run
```

### **5. Soumettre une Pull Request**
1. Poussez votre branche :
   ```bash
   git push origin feature/nom-de-la-fonction
   ```
2. Ouvrez une PR sur GitHub avec une description claire des changements.

### **Règles de contribution**
- **Style de code** : Respectez le style K&R (indentation, accolades).
- **Documentation** : Ajoutez des commentaires pour les fonctions complexes.
- **Tests** : Vérifiez que votre code compile et fonctionne dans QEMU.

---

## **Roadmap**
Voici les étapes prévues pour les prochaines versions :

| Version | Objectif                          | Statut       |
|---------|-----------------------------------|--------------|
| v0.1    | Prototype bare metal (x86)        | ✅ Terminé   |
| v0.2    | Gestion basique de la mémoire     | 🔄 En cours  |
| v0.3    | Système de fichiers (FAT16)       | 📝 Planifié  |
| v0.4    | Multitâche (coopératif)           | 📝 Planifié  |
| v1.0    | Support des périphériques USB     | 🚀 À long terme |

### **Fonctionnalités en développement**
- **Gestion de la mémoire** : Allocation dynamique (`malloc`/`free`).
- **Système de fichiers** : Lecture/écriture sur disque (FAT16).
- **Interruptions** : Gestion avancée des IRQ (horloge, clavier).
- **Réseau** : Pilote basique pour carte Ethernet (future version).

### **Idées pour contributions externes**
- Ajout d'un shell minimal.
- Support du mode graphique (VESA).
- Portage sur ARM (Raspberry Pi).

---

## **Licence**
MaxOS est distribué sous la licence **MIT** (voir `LICENSE`).
Vous êtes libre de modifier et redistribuer le code, à condition de conserver la notice de copyright.

---
**Contact** : [votre.email@example.com]
**Dépôt GitHub** : [https://github.com/votre-utilisateur/maxos](https://github.com/votre-utilisateur/maxos)
```

---

### **Points clés de cette documentation** :

---
*MaxOS AI v18.0*
