# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fichiers** : 57 (C) | 19 (ASM) | **Sortie** : Boot x86, VGA texte 80x25

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental conçu pour exécuter un environnement texte minimal sur architecture x86. Il sert de banc d'essai pour comprendre les concepts fondamentaux des OS (bootloader, gestion mémoire, drivers basiques).

> ⚠️ **Avertissement** : Ce projet est un prototype éducatif. Ne l'utilisez pas en production.

---

## **🔧 Guide Développeur**

### **1️⃣ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation croisée avec `gcc` et `nasm`.

#### **Prérequis**
- **Outils** :
  - `gcc` (version cross-compilée pour x86, ex: `i686-elf-gcc`)
  - `nasm` (assembleur x86)
  - `ld` (linker)
  - `qemu-system-x86` (pour les tests)
  - `make` (GNU Make)

- **Bibliothèques** :
  Aucune dépendance externe (code pur C/ASM).

#### **Étapes**
1. **Configurer l'environnement** :
   ```bash
   export PREFIX=i686-elf-  # Préfixe pour les outils cross-compilés
   export PATH=$PATH:/chemin/vers/les/outils/cross/bin
   ```

2. **Compiler** :
   ```bash
   make clean && make
   ```
   - **Sortie** : `maxos.bin` (image bootable).

3. **Options avancées** :
   - `make debug` : Active les symboles de débogage (GDB).
   - `make iso` : Génère une image ISO bootable (nécessite `grub-mkrescue`).

---

### **2️⃣ Test avec QEMU**
QEMU permet d'émuler un environnement x86 pour tester MaxOS sans matériel physique.

#### **Lancement de base**
```bash
qemu-system-x86_64 -drive format=raw,file=maxos.bin -vga std
```
- `-vga std` : Active l'émulation VGA standard (80x25 texte).
- `-serial mon:stdio` : Redirige la sortie série vers le terminal.

#### **Débogage avec GDB**
1. **Lancer QEMU en mode debug** :
   ```bash
   qemu-system-x86_64 -s -S -drive format=raw,file=maxos.bin -vga std
   ```
   - `-s` : Active le serveur GDB sur le port 1234.
   - `-S` : Met en pause l'exécution jusqu'à connexion GDB.

2. **Connecter GDB** :
   ```bash
   i686-elf-gdb maxos.elf
   (gdb) target remote localhost:1234
   (gdb) continue
   ```

#### **Dépannage**
- **Écran noir** : Vérifiez que `maxos.bin` est bien généré et que QEMU utilise le bon mode VGA.
- **Erreurs de segmentation** : Utilisez `gdb` pour inspecter la pile d'appels.

---

### **3️⃣ Structure des Fichiers**
```
maxos/
├── boot/               # Code de boot (ASM)
│   ├── boot.asm        # Bootloader (charge le noyau)
│   └── gdt.asm         # Table des descripteurs globaux
├── kernel/             # Noyau (C)
│   ├── main.c          # Point d'entrée du noyau
│   ├── drivers/        # Pilotes matériels
│   │   ├── vga.c       # Gestion de l'affichage texte
│   │   └── keyboard.c  # Pilote clavier PS/2
│   ├── mm/             # Gestion mémoire
│   │   └── paging.c    # Pagination basique
│   └── lib/            # Bibliothèques utilitaires
│       ├── string.c    # Fonctions de chaîne
│       └── stdio.c     # Entrées/sorties
├── include/            # En-têtes
│   ├── kernel.h        # Définitions globales
│   └── drivers/        # En-têtes des drivers
├── Makefile            # Règles de compilation
├── linker.ld           # Script de linkage
└── README.md           # Documentation
```

#### **Détails clés**
- **Bootloader** (`boot.asm`) :
  - Charge le noyau en mémoire à l'adresse `0x1000`.
  - Passe en mode protégé (32 bits) via la GDT.
- **Noyau** (`main.c`) :
  - Initialise les drivers (VGA, clavier).
  - Boucle principale : attend les entrées clavier et affiche du texte.
- **Drivers** :
  - `vga.c` : Écriture en mémoire vidéo (0xB8000).
  - `keyboard.c` : Gestion des interruptions IRQ1.

---

### **4️⃣ Contribuer**
MaxOS accepte les contributions via **GitHub Pull Requests**. Voici comment participer :

#### **Processus**
1. **Forker le dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

2. **Créer une branche** :
   ```bash
   git checkout -b feature/nom-de-la-fonction
   ```

3. **Implémenter la fonctionnalité** :
   - Respectez le style de code (indentation, noms de variables).
   - Ajoutez des commentaires pour les parties complexes.
   - Testez avec `make` et QEMU.

4. **Soumettre une PR** :
   - Décrivez clairement les changements.
   - Liez les issues pertinentes (ex: `#12`).

#### **Bonnes pratiques**
- **Code** :
  - Utilisez `static` pour les fonctions internes.
  - Évitez les allocations dynamiques (pas de `malloc` dans le noyau).
- **Documentation** :
  - Mettez à jour le `README.md` si nécessaire.
  - Ajoutez des commentaires dans le code pour les algorithmes critiques.

#### **Exemple de contribution**
- **Ajouter un driver pour le port série** :
  ```c
  // kernel/drivers/serial.c
  void serial_init() {
      outb(PORT_COM1 + 1, 0x00); // Désactive les interruptions
      outb(PORT_COM1 + 3, 0x80); // Active le DLAB
      outb(PORT_COM1 + 0, 0x03); // Baud rate 38400
      outb(PORT_COM1 + 3, 0x03); // 8 bits, pas de parité
  }
  ```

---

### **5️⃣ Roadmap**
Voici les objectifs futurs pour MaxOS, classés par priorité :

| **Phase** | **Objectif**                          | **Statut** | **Détails**                          |
|-----------|---------------------------------------|------------|--------------------------------------|
| **1**     | Bootloader fonctionnel                | ✅         | Mode texte 80x25, gestion clavier    |
| **2**     | Gestion mémoire basique               | ⚠️         | Pagination, heap simple              |
| **3**     | Système de fichiers (FAT16)           | 🚧         | Pilote disque IDE/ATA                |
| **4**     | Multitâche préemptif                 | 📝         | TSS, scheduler basique               |
| **5**     | Support réseau (TCP/IP)               | 📝         | Pilote NE2000 (émulé dans QEMU)     |
| **6**     | Interface utilisateur graphique       | 📝         | Mode VESA 320x200                    |
| **7**     | Sécurité (ASLR, SELinux-like)         | 📝         | Protection mémoire                   |

#### **Comment aider ?**
- **Priorité 2** : Implémenter un allocateur de mémoire (buddy system).
- **Priorité 3** : Écrire un pilote pour le clavier USB (nécessite un

---
*MaxOS AI v18.0*
