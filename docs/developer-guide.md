# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

```markdown
# **Documentation Technique MaxOS**
*Un système d'exploitation minimaliste pour x86 en mode texte*

**Version** : 0.1 (Prototype bare metal)
**Score** : 35/100
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage en mode texte VGA 80x25
- 76 fichiers en C, 23 en ASM

---

## **1. Guide Développeur**

### **1.1 Prérequis**
Pour compiler et tester MaxOS, vous aurez besoin de :
- **Compilateur** : `gcc` (version 10+) ou `clang`
- **Assembleur** : `nasm` (pour les fichiers `.asm`)
- **Émulateur** : `qemu-system-x86_64` (pour les tests)
- **Outils** : `make`, `ld` (linker GNU)
- **Bibliothèques** : Aucune dépendance externe (sauf pour QEMU)

---

### **1.2 Compilation**

#### **Étape 1 : Cloner le dépôt**
```bash
git clone https://github.com/votre-utilisateur/maxos.git
cd maxos
```

#### **Étape 2 : Compiler le noyau**
MaxOS utilise un `Makefile` pour automatiser la compilation. Exécutez :
```bash
make
```
**Options disponibles** :
- `make clean` : Nettoie les fichiers objets et exécutables.
- `make debug` : Active les logs de débogage (si implémenté).
- `make iso` : Génère une image ISO bootable (nécessite `xorriso`).

**Détails techniques** :
- Le noyau est compilé en **mode 32 bits** (`-m32` pour GCC).
- Les fichiers `.c` sont compilés avec `-ffreestanding -nostdlib`.
- Le linker (`ld`) utilise un script `linker.ld` pour générer l'exécutable binaire.

---

### **1.3 Test avec QEMU**

#### **Lancement de base**
Pour tester MaxOS dans QEMU :
```bash
make run
```
**Options QEMU** :
- `-serial stdio` : Affiche la sortie série dans le terminal.
- `-display none` : Désactive l'affichage graphique (utile pour le mode texte).
- `-d int` : Active les logs d'interruptions (pour le débogage).

#### **Débogage avancé**
- **GDB** : Lancez QEMU avec `-s -S` pour permettre le débogage :
  ```bash
  qemu-system-x86_64 -kernel maxos.bin -s -S &
  gdb -ex "target remote localhost:1234" -ex "symbol-file maxos.elf"
  ```
- **Logs** : Utilisez `printf` dans le code C ou des instructions `xchg bx, bx` en ASM pour des breakpoints matériels.

---

## **2. Structure des Fichiers**

```
maxos/
├── Makefile                # Script de compilation
├── linker.ld               # Script du linker (adresse de chargement, sections)
├── src/
│   ├── kernel/             # Noyau principal
│   │   ├── main.c          # Point d'entrée (boot.asm appelle main())
│   │   ├── drivers/        # Pilotes (VGA, clavier, etc.)
│   │   │   ├── vga.c       # Gestion de l'affichage texte
│   │   │   └── keyboard.c  # Gestion du clavier PS/2
│   │   ├── memory/         # Gestion mémoire (si implémenté)
│   │   └── ...
│   ├── boot/               # Code de boot
│   │   ├── boot.asm        # Code assembleur de démarrage (mode réel)
│   │   └── gdt.asm         # Initialisation de la GDT (si protégé)
│   └── lib/                # Bibliothèques utilitaires
│       ├── stdio.c         # Fonctions d'affichage (printf)
│       └── ...
├── include/                # En-têtes (.h)
├── tools/                  # Scripts utilitaires
└── docs/                   # Documentation
```

### **Fichiers Clés**
| Fichier          | Rôle                                                                 |
|------------------|----------------------------------------------------------------------|
| `boot.asm`       | Passe en mode protégé (si nécessaire) et charge le noyau.           |
| `main.c`         | Point d'entrée du noyau (appelé après le boot).                     |
| `vga.c`          | Gère l'affichage texte (écriture, couleurs, curseur).               |
| `keyboard.c`     | Pilote le clavier PS/2 (interruptions IRQ1).                        |
| `linker.ld`      | Définit les sections mémoire (`.text`, `.data`, `.bss`).            |

---

## **3. Contribuer à MaxOS**

### **3.1 Bonnes Pratiques**
- **Style de code** :
  - Respectez le style **K&R** pour le C.
  - Utilisez des commentaires en français pour les fonctions critiques.
  - Nommez les variables de manière explicite (`uint32_t gdt_size`).
- **Commits** :
  - Messages clairs et concis (ex: `Ajout du pilote clavier PS/2`).
  - Une fonctionnalité par commit.
- **Tests** :
  - Testez toujours avec `make run` avant de pousser.
  - Ajoutez des tests unitaires si possible (ex: pour `vga.c`).

### **3.2 Processus de Contribution**
1. **Fork** le dépôt et clonez votre fork.
2. Créez une branche pour votre contribution :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
3. Implémentez votre code et testez-le.
4. Poussez vos changements :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
5. Ouvrez une **Pull Request** (PR) sur le dépôt principal avec une description détaillée.

### **3.3 Exemple de Contribution**
**Ajout d'un pilote pour le port série (COM1)** :
1. Créez `drivers/serial.c` :
   ```c
   #include <stdint.h>
   #include "io.h"

   void serial_init() {
       outb(0x3F8 + 1, 0x00); // Désactive les interruptions
       outb(0x3F8 + 3, 0x80); // Active le bit DLAB
       outb(0x3F8 + 0, 0x03); // Baud rate 38400 (LSB)
       outb(0x3F8 + 1, 0x00); // Baud rate 38400 (MSB)
       outb(0x3F8 + 3, 0x03); // 8 bits, pas de parité, 1 stop bit
   }

   void serial_putc(char c) {
       while ((inb(0x3F8 + 5) & 0x20) == 0); // Attend que le buffer soit prêt
       outb(0x3F8, c);
   }
   ```
2. Ajoutez l'en-tête dans `include/serial.h`.
3. Modifiez `main.c` pour appeler `serial_init()`.
4. Testez avec `make run` et vérifiez la sortie série avec `screen` :
   ```bash
   screen /dev/ttyS0 115200
   ```

---

## **4. Roadmap**

### **Phase 1 : Prototype Bare Metal (0.1 - 0.3)**
- [x] Boot en mode réel (16 bits).
- [x] Passage en mode protégé (32 bits).
- [x] Affichage texte VGA 80x25.
- [x] Gestion basique du clavier PS/2.
- [ ] **Objectif 0.3** : Interruptions matérielles (IRQ0 pour le timer).

### **Phase 2 : Noyau Minimal (0.4 - 0.6)**
- [ ] Gestion mémoire (paging basique).
- [ ] Système de fichiers simplifié (FAT16).
- [ ] Pilotes pour le disque dur (ATA PIO).
- [ ] **Objectif 0.6** : Shell minimal avec commandes `echo`, `ls`.

### **Phase 3 : Multitâche (0.7 - 1.0)**
- [ ] Ordonnanceur de tâches (round-robin).
- [ ] Gestion des processus (fork, exec).
- [ ] **Objectif 1.0** : Premier OS utilisable pour des

---
*MaxOS AI v18.0*
