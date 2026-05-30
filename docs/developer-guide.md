# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée de manière professionnelle et adaptée à un niveau *Prototype bare metal*.

---

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fichiers** : 71 (C) | 23 (ASM)

---

## **📌 Table des matières**
1. [Prérequis](#prérequis)
2. [Compilation](#compilation)
3. [Test avec QEMU](#test-avec-qemu)
4. [Structure des fichiers](#structure-des-fichiers)
5. [Contribuer](#contribuer)
6. [Roadmap](#roadmap)
7. [Licence](#licence)

---

## **🔧 Prérequis**
Pour compiler et tester MaxOS, vous aurez besoin de :

| Composant          | Version minimale | Installation (Linux)                     |
|--------------------|------------------|------------------------------------------|
| **GCC**            | 11+              | `sudo apt install build-essential`       |
| **NASM**           | 2.15+            | `sudo apt install nasm`                  |
| **QEMU**           | 6.2+             | `sudo apt install qemu-system-x86`       |
| **GNU Make**       | 4.3+             | `sudo apt install make`                  |
| **GNU Binutils**   | 2.38+            | Inclus dans `build-essential`            |
| **GNU Coreutils**  | 8.32+            | Inclus dans `build-essential`            |

> **Note** : Sous Windows, utilisez **WSL** ou **MSYS2** pour une compatibilité optimale.

---

## **🛠️ Compilation**
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

### **3. Vérifier la sortie**
- **`maxos.bin`** : Image binaire du noyau (format ELF).
- **`maxos.iso`** : Image ISO bootable (optionnelle, pour tests physiques).

> **Options avancées** :
> - `make debug` : Active les symboles de débogage (GDB).
> - `make run` : Lance QEMU après compilation (voir [Test avec QEMU](#test-avec-qemu)).

---

## **🖥️ Test avec QEMU**
MaxOS est conçu pour être testé dans un émulateur. Voici comment lancer le système :

### **1. Lancer QEMU en mode texte**
```bash
make run
```
> **Options par défaut** :
> - `-serial stdio` : Affiche la sortie VGA dans le terminal.
> - `-display none` : Désactive l'affichage graphique (mode texte uniquement).
> - `-m 128M` : Alloue 128 Mo de RAM.

### **2. Commandes utiles dans QEMU**
| Commande       | Description                          |
|----------------|--------------------------------------|
| `Ctrl+A C`     | Basculer vers la console QEMU.       |
| `Ctrl+A X`     | Quitter QEMU.                       |
| `Ctrl+A H`     | Afficher l'aide des raccourcis.     |

### **3. Débogage avec GDB**
Pour déboguer le noyau :
```bash
make debug
```
Puis, dans un autre terminal :
```bash
gdb -q maxos.bin
(gdb) target remote localhost:1234
(gdb) continue
```

---

## **📂 Structure des fichiers**
MaxOS suit une architecture **modulaire** avec les dossiers principaux suivants :

```
maxos/
├── **boot/**          # Code de démarrage (ASM)
│   ├── boot.asm       # Chargeur de démarrage (MBR)
│   └── kernel_entry.asm # Point d'entrée du noyau
├── **kernel/**        # Noyau principal (C)
│   ├── main.c         # Point d'entrée du noyau
│   ├── drivers/       # Pilotes matériels
│   │   ├── vga.c      # Pilote VGA texte (80x25)
│   │   └── keyboard.c # Pilote clavier PS/2
│   ├── lib/           # Bibliothèques utilitaires
│   │   ├── string.c   # Fonctions de chaîne
│   │   └── stdio.c    # Entrée/sortie standard
│   └── mm/            # Gestion mémoire
│       └── paging.c   # Initialisation de la pagination
├── **include/**       # En-têtes C
│   ├── kernel.h       # Déclarations globales
│   └── drivers/       # En-têtes des pilotes
├── **tools/**         # Outils de build
│   ├── linker.ld      # Script de liaison (LD)
│   └── Makefile       # Règles de compilation
├── **docs/**          # Documentation
└── **LICENSE**        # Licence MIT
```

### **🔹 Fichiers clés**
| Fichier               | Rôle                                                                 |
|-----------------------|----------------------------------------------------------------------|
| `boot/boot.asm`       | Charge le noyau en mémoire (secteur 0 du disque).                   |
| `kernel/main.c`       | Point d'entrée du noyau (initialisation matérielle et boucle principale). |
| `drivers/vga.c`       | Gère l'affichage en mode texte (80x25).                             |
| `tools/linker.ld`     | Script de liaison pour générer une image binaire.                   |

---

## **🤝 Contribuer**
MaxOS est un projet **open source** et accueille les contributions ! Voici comment participer :

### **1. Forker le dépôt**
1. Créez un fork sur [GitHub](https://github.com/votre-utilisateur/maxos/fork).
2. Clonez votre fork :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

### **2. Créer une branche**
```bash
git checkout -b feature/ma-nouvelle-fonctionnalité
```

### **3. Implémenter votre contribution**
- **Nouveau pilote** : Ajoutez un fichier dans `kernel/drivers/` et déclarez-le dans `include/drivers/`.
- **Optimisation** : Documentez vos changements dans les commentaires du code.
- **Correction de bug** : Ouvrez une *issue* avant de coder pour discuter de la solution.

### **4. Soumettre une Pull Request (PR)**
1. Poussez vos changements :
   ```bash
   git add .
   git commit -m "feat: ajout du pilote IDE"
   git push origin feature/ma-nouvelle-fonctionnalité
   ```
2. Ouvrez une PR sur le dépôt principal.
3. Respectez le **style de code** (indentation, noms de variables, etc.).

### **📌 Bonnes pratiques**
- **Tests** : Vérifiez que votre code compile (`make`) et fonctionne dans QEMU.
- **Documentation** : Mettez à jour le README ou ajoutez des commentaires dans le code.
- **Style** : Utilisez `clang-format` pour uniformiser le code :
  ```bash
  clang-format -i kernel/main.c
  ```

---

## **🗺️ Roadmap**
MaxOS est en phase de **prototype bare metal**. Voici les objectifs à court et moyen terme :

### **🔹 Phase 1 : Stabilisation (0-6 mois)**
| Objectif                     | Statut       | Détails                                  |
|------------------------------|--------------|------------------------------------------|
| **Bootloader fiable**        | ✅ Terminé   | Support du MBR et passage en mode protégé. |
| **Gestion mémoire basique**  | ✅ Terminé   | Pagination et allocation dynamique.       |
| **Pilotes VGA et clavier**   | ✅ Terminé   | Affichage 80x25 et entrée clavier.       |
| **Système de fichiers**      | ⏳ En cours  | Support FAT16/32 pour le stockage.       |
| **Multitâche coopératif**    | ❌ À faire   | Implémentation des *tasks* et *scheduler*. |

### **🔹 Phase 2 : Fonctionnalités avancées (6

---
*MaxOS AI v18.0*
