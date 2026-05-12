# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 (Prototype bare metal)
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage VGA texte 80x25
- **Fichiers** : 51 en C, 18 en ASM

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
- **Bibliothèques** : Aucune dépendance externe (système minimaliste)

> **Note** : Sous Linux, installez les dépendances via :
> ```bash
> sudo apt install build-essential nasm qemu-system-x86
> ```

---

## **🛠️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation.

### **Étapes :**
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

2. Compilez le noyau :
   ```bash
   make
   ```
   - **Sortie** : `maxos.bin` (image binaire bootable)

3. (Optionnel) Nettoyez les fichiers temporaires :
   ```bash
   make clean
   ```

### **Détails Techniques :**
- **Fichiers compilés** :
  - Noyau (`kernel.c` → `kernel.o` → `kernel.elf`)
  - Bootloader (`boot.asm` → `boot.bin`)
- **Linker Script** : `linker.ld` (définit la mémoire et les sections)
- **Options de compilation** :
  - `-ffreestanding` : Désactive les dépendances système.
  - `-m32` : Force la compilation en 32 bits (x86).
  - `-nostdlib` : Exclut la libc standard.

---

## **🧪 Test avec QEMU**
MaxOS est conçu pour être testé dans **QEMU**, un émulateur x86.

### **Commande de base :**
```bash
qemu-system-x86_64 -fda maxos.bin -display sdl
```
- `-fda` : Charge l'image comme un disque bootable.
- `-display sdl` : Affiche la sortie VGA en mode texte.

### **Options Avancées :**
| Option | Description |
|--------|-------------|
| `-serial stdio` | Redirige la sortie série vers le terminal. |
| `-m 128M` | Alloue 128 Mo de RAM (par défaut : 128 Mo). |
| `-d int` | Active les logs des interruptions (debug). |

### **Debugging avec GDB :**
1. Lancez QEMU en mode debug :
   ```bash
   qemu-system-x86_64 -fda maxos.bin -s -S &
   ```
   - `-s` : Active le serveur GDB sur le port `1234`.
   - `-S` : Met en pause l'exécution.

2. Connectez GDB :
   ```bash
   gdb maxos.elf
   (gdb) target remote localhost:1234
   (gdb) continue
   ```

---

## **📂 Structure des Fichiers**
```
maxos/
├── boot/               # Code de boot (ASM)
│   ├── boot.asm        # Bootloader principal
│   └── gdt.asm         # Table des descripteurs globaux
├── kernel/             # Noyau (C)
│   ├── kernel.c        # Point d'entrée du noyau
│   ├── drivers/        # Pilotes matériels
│   │   └── vga.c       # Gestion de l'affichage VGA
│   └── lib/            # Bibliothèques utilitaires
│       ├── string.c    # Fonctions de chaîne
│       └── io.c        # Ports d'E/S
├── include/            # En-têtes
│   ├── kernel.h        # Déclarations du noyau
│   └── stdint.h        # Types entiers standard
├── Makefile            # Règles de compilation
├── linker.ld           # Script de linkage
└── README.md           # Documentation
```

### **Fichiers Clés :**
| Fichier | Rôle |
|---------|------|
| `boot.asm` | Initialise le CPU en mode protégé et charge le noyau. |
| `kernel.c` | Point d'entrée (`main()`), initialise les périphériques. |
| `vga.c` | Gère l'affichage texte 80x25 via les ports VGA. |
| `gdt.asm` | Définit les segments mémoire (code, données, etc.). |

---

## **🤝 Contribuer**
MaxOS est un projet open-source. Voici comment contribuer :

### **1. Fork & Clone**
```bash
git clone https://github.com/votre-utilisateur/maxos.git
cd maxos
git checkout -b feature/ma-nouvelle-fonctionnalité
```

### **2. Ajouter une Fonctionnalité**
- **Nouveau pilote** : Placez-le dans `kernel/drivers/`.
- **Nouvelle bibliothèque** : Ajoutez-la dans `kernel/lib/`.
- **Correction de bug** : Ouvrez une *issue* avant de coder.

### **3. Soumettre une Pull Request (PR)**
1. Testez vos modifications :
   ```bash
   make clean && make
   qemu-system-x86_64 -fda maxos.bin
   ```
2. Committez vos changements :
   ```bash
   git add .
   git commit -m "feat: ajout du support du clavier PS/2"
   git push origin feature/ma-nouvelle-fonctionnalité
   ```
3. Ouvrez une PR sur GitHub avec une description claire.

### **📜 Bonnes Pratiques :**
- **Code** : Respectez le style (indentation, noms de variables).
- **Documentation** : Ajoutez des commentaires pour les fonctions complexes.
- **Tests** : Vérifiez que le noyau boot toujours après vos modifications.

---

## **🗺️ Roadmap**
MaxOS est en phase de **prototype bare metal**. Voici les étapes prévues :

| Phase | Objectif | Statut |
|-------|----------|--------|
| **v0.1** | Boot basique + VGA | ✅ Terminé |
| **v0.2** | Gestion des interruptions (IRQ) | 🔄 En cours |
| **v0.3** | Pilotes clavier/souris | 🚧 Planifié |
| **v0.4** | Système de fichiers (FAT16) | 📅 2024 Q3 |
| **v0.5** | Multitâche (scheduling) | 📅 2024 Q4 |
| **v1.0** | OS utilisable (shell basique) | 🎯 2025 |

### **Fonctionnalités Long Terme :**
- Support du **multiprocesseur (SMP)**.
- **Réseau** (pilote Ethernet).
- **Graphismes** (mode VESA).
- **Compatibilité** avec les binaires ELF.

---

## **📜 Licence**
MaxOS est distribué sous la **licence MIT** :
- Permission de modifier et redistribuer.
- Pas de garantie (AS IS).
- Attribution requise (mentionnez les auteurs).

> **Auteurs** : [Votre Nom] et contributeurs.
> **Contact** : votre@email.com

---

## **🔗 Ressources Utiles**
- [OSDev Wiki](https://wiki.osdev.org/) (Référence pour le développement OS).
- [Intel Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) (

---
*MaxOS AI v18.0*
