# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée selon vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage VGA texte 80x25
- 43 fichiers C | 14 fichiers ASM

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
Avant de compiler ou tester MaxOS, assurez-vous d'avoir installé :
- **Compilateur** : `gcc` (version ≥ 10) ou `clang`
- **Assembleur** : `nasm` (pour les fichiers `.asm`)
- **Linker** : `ld` (GNU Linker)
- **Émulateur** : `qemu-system-x86_64` (pour les tests)
- **Outils** : `make` (recommandé), `dd` (optionnel pour création d'image disque)

**Installation sous Linux (Debian/Ubuntu)** :
```bash
sudo apt update && sudo apt install -y build-essential nasm qemu-system-x86 grub2 xorriso
```

---

## **🛠️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation.

### **Étapes de compilation**
1. **Nettoyer les anciens artefacts** (optionnel) :
   ```bash
   make clean
   ```
2. **Compiler le noyau** :
   ```bash
   make
   ```
   - Le Makefile génère :
     - `kernel.bin` (noyau binaire)
     - `kernel.elf` (version avec symboles de débogage)
     - `os.iso` (image ISO bootable, si `grub-mkrescue` est installé)

### **Options de compilation**
| Option | Description |
|--------|-------------|
| `make debug` | Active les symboles de débogage (-g) |
| `make release` | Optimise le code (-O2) |
| `make run` | Compile et lance QEMU automatiquement |

**Exemple** :
```bash
make debug && make run
```

---

## **🧪 Test avec QEMU**
MaxOS est conçu pour être testé dans **QEMU**, un émulateur x86.

### **Lancer MaxOS dans QEMU**
```bash
make run
```
- **Options avancées** :
  ```bash
  qemu-system-x86_64 -drive format=raw,file=os.img -m 128M -serial stdio
  ```
  - `-m 128M` : Alloue 128 Mo de RAM.
  - `-serial stdio` : Redirige la sortie série vers le terminal.

### **Débogage avec GDB**
1. **Lancer QEMU en mode debug** :
   ```bash
   qemu-system-x86_64 -s -S -kernel kernel.bin
   ```
2. **Connecter GDB** :
   ```bash
   gdb kernel.elf
   (gdb) target remote :1234
   (gdb) continue
   ```

---

## **📂 Structure des Fichiers**
```
maxos/
├── Makefile                # Script de compilation
├── kernel/                 # Code source du noyau
│   ├── main.c              # Point d'entrée
│   ├── drivers/            # Pilotes matériels
│   │   ├── vga.c           # Affichage VGA
│   │   └── keyboard.c      # Clavier PS/2
│   ├── lib/                # Bibliothèques utilitaires
│   │   ├── string.c        # Fonctions de chaîne
│   │   └── stdio.c         # Entrée/sortie
│   └── arch/x86/           # Code spécifique à l'architecture
│       ├── boot.asm        # Bootloader (secteur 0)
│       ├── gdt.asm         # Table des descripteurs globaux
│       └── isr.asm         # Gestion des interruptions
├── include/                # En-têtes
│   ├── kernel.h            # Définitions globales
│   └── drivers/            # En-têtes des pilotes
├── tools/                  # Scripts utilitaires
│   └── mkiso.sh            # Création d'une image ISO
└── docs/                   # Documentation
```

### **Fichiers Clés**
| Fichier | Rôle |
|---------|------|
| `boot.asm` | Charge le noyau en mémoire (mode réel → protégé) |
| `main.c` | Point d'entrée du noyau (boucle principale) |
| `vga.c` | Gestion de l'affichage texte (80x25) |
| `gdt.asm` | Initialise la Global Descriptor Table (GDT) |
| `Makefile` | Automatise la compilation et le linking |

---

## **🤝 Contribuer**
MaxOS est un projet open-source. Voici comment contribuer :

### **1. Forker le dépôt**
- Créez un fork sur [GitHub/GitLab](https://github.com/votre-utilisateur/maxos).
- Clonez votre fork :
  ```bash
  git clone https://github.com/votre-utilisateur/maxos.git
  cd maxos
  ```

### **2. Créer une branche**
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### **3. Soumettre une Pull Request**
1. **Testez vos modifications** :
   ```bash
   make && make run
   ```
2. **Validez les changements** :
   ```bash
   git add .
   git commit -m "Ajout de [FEATURE] : description"
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
3. **Ouvrez une PR** sur le dépôt principal.

### **📌 Bonnes Pratiques**
- **Code** :
  - Respectez le style (indentation à 4 espaces, noms de variables explicites).
  - Documentez les fonctions avec des commentaires en français.
- **Tests** :
  - Testez toujours dans QEMU avant de soumettre une PR.
  - Utilisez `gdb` pour déboguer les crashes.

---

## **🗺️ Roadmap**
MaxOS est en phase de **prototype bare metal**. Voici les étapes prévues :

| Phase | Objectif | Statut |
|-------|----------|--------|
| **Phase 1** (Actuelle) | Boot x86 + VGA 80x25 | ✅ Complété |
| **Phase 2** | Gestion des interruptions (IRQ) | 🔄 En cours |
| **Phase 3** | Pilotes de base (clavier, disque) | 🚧 Planifié |
| **Phase 4** | Système de fichiers (FAT32) | 📝 À étudier |
| **Phase 5** | Multitâche préemptif | 🔮 Futur |

### **Fonctionnalités à long terme**
- Support du **multitâche** (avec un scheduler simple).
- **Gestion mémoire** (paging, heap dynamique).
- **Réseau** (pilote Ethernet basique).
- **Compatibilité** avec les outils GNU (GCC cross-compiler).

---

## **📜 Licence**
MaxOS est distribué sous la **licence MIT** (voir `LICENSE`).
Vous êtes libre de :
- Utiliser, copier, modifier et distribuer le code.
- Intégrer MaxOS dans des projets commerciaux.

**Attribution** : Incluez la licence et les copyrights dans les distributions.

---

## **📬 Contact & Support**
- **Problèmes** : Ouvrez une [issue](https://github.com/organisation/maxos/issues).
- **Discussions** : Rejoignez le [Discord](https://discord.gg/maxos) (lien fictif).
- **Auteurs** : [Votre Nom](mailto:votre@email.com)

---
*Documentation générée avec ❤️ pour les développeurs OS.*
```

---

### **Points forts de cette documentation** :
1. **Structure claire** : Sections bien définies avec des tableaux pour les options.
2. **Pratique** : Commandes prêtes à l'emploi et exemples concrets

---
*MaxOS AI v18.0*
