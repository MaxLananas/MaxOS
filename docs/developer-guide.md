# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*

**Score** : 35/100 (Prototype bare metal)
**Fichiers** : 61 (C) | 21 (ASM)
**Dernière mise à jour** : [Date]

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental conçu pour :
- Démarrer sur architecture x86 (32 bits).
- Afficher un terminal texte en mode VGA 80x25.
- Servir de base pour l'apprentissage des concepts OS (interruptions, gestion mémoire, etc.).

Ce guide couvre les aspects techniques essentiels pour les développeurs souhaitant contribuer ou tester le projet.

---

## **🔧 Prérequis**
- **Compilateur** : `gcc` (version 9+) ou `clang` avec support cross-compilation.
- **Assembleur** : `nasm` (pour les fichiers `.asm`).
- **Émulateur** : `QEMU` (version 6.0+ recommandée).
- **Outils** : `make`, `ld` (GNU Linker), `objcopy`.
- **Bibliothèques** : Aucune dépendance externe (sauf pour QEMU).

---

## **🛠️ 1. Compilation du Projet**

### **Structure des fichiers**
```
maxos/
├── boot/               # Code de démarrage (ASM)
│   ├── boot.asm        # Chargeur de démarrage (MBR)
│   └── kernel_entry.asm # Point d'entrée du noyau
├── kernel/             # Code du noyau (C)
│   ├── main.c          # Fonction principale
│   ├── drivers/        # Pilotes (VGA, clavier)
│   ├── lib/            # Bibliothèques utilitaires
│   └── ...
├── include/            # En-têtes (.h)
├── scripts/            # Scripts de build
│   └── build.sh        # Script de compilation principal
├── Makefile            # Règles de compilation
└── README.md           # Documentation utilisateur
```

### **Étapes de compilation**
1. **Nettoyer les anciens builds** (optionnel) :
   ```bash
   make clean
   ```

2. **Compiler le noyau** :
   ```bash
   make
   ```
   - Le script `build.sh` utilise `nasm` pour assembler les fichiers `.asm` et `gcc` pour compiler le C.
   - Le résultat est un binaire `kernel.bin` (format ELF brut).

3. **Générer l'image disque** (pour QEMU) :
   ```bash
   make disk
   ```
   - Crée un fichier `maxos.img` (disquette 1.44 Mo) avec le noyau en secteur 0.

---

## **🧪 2. Test avec QEMU**

### **Lancer MaxOS dans QEMU**
```bash
qemu-system-i386 -fda maxos.img -monitor stdio
```
- `-fda` : Charge l'image disque comme une disquette.
- `-monitor stdio` : Permet d'interagir avec QEMU (Ctrl+A puis X pour quitter).

### **Débogage avancé**
- **GDB** : Pour déboguer le noyau :
  ```bash
  qemu-system-i386 -fda maxos.img -s -S &
  gdb -ex "target remote localhost:1234" -ex "symbol-file kernel.elf"
  ```
- **Logs** : Ajoutez `-d int,cpu_reset` à QEMU pour afficher les interruptions.

### **Résolution des problèmes courants**
| Problème | Solution |
|----------|----------|
| Écran noir | Vérifiez que `boot.asm` charge correctement le noyau. |
| Erreur de segmentation | Activez les interruptions matérielles (PIC/APIC). |
| QEMU ne démarre pas | Utilisez `-drive format=raw,file=maxos.img` (alternative). |

---

## **📂 3. Structure du Code**

### **Fichiers clés**
| Chemin | Description |
|--------|-------------|
| `boot/boot.asm` | Charge le noyau en mémoire (via `BIOS INT 0x13`). |
| `kernel/main.c` | Point d'entrée du noyau (`kernel_main()`). |
| `kernel/drivers/vga.c` | Gestion de l'affichage texte (80x25). |
| `include/maxos.h` | Définitions globales (registres, macros). |

### **Conventions de codage**
- **Nommage** :
  - Variables : `snake_case` (ex: `current_cursor_pos`).
  - Fonctions : `camelCase` (ex: `initPic()`).
- **Style** : Respectez le style K&R (accolades sur la même ligne).
- **Documentation** : Utilisez des commentaires `/* ... */` pour les blocs et `//` pour les lignes.

### **Gestion des interruptions**
- Le noyau configure le **PIC (8259A)** pour rediriger les IRQ vers les interruptions logicielles (0x20-0x2F).
- Exemple d'interruption clavier :
  ```c
  // kernel/drivers/keyboard.c
  void keyboard_handler() {
      uint8_t scancode = inb(0x60); // Lecture du port PS/2
      // Traitement du scancode...
  }
  ```

---

## **🤝 4. Contribuer au Projet**

### **Processus de contribution**
1. **Fork** le dépôt sur GitHub/GitLab.
2. **Créez une branche** pour votre feature :
   ```bash
   git checkout -b feature/ma_nouvelle_fonction
   ```
3. **Respectez les conventions** :
   - Testez vos modifications avec `make test`.
   - Ajoutez des tests unitaires si possible (ex: pour `lib/string.c`).
4. **Soumettez une Pull Request** avec une description claire.

### **Bonnes pratiques**
- **Commits** : Messages clairs et concis (ex: "Ajout support PS/2 pour le clavier").
- **Code Review** : Soyez prêt à itérer sur les retours.
- **Documentation** : Mettez à jour le README ou ce fichier si nécessaire.

### **Exemple de contribution**
- **Ajouter un pilote pour le port série** :
  1. Créez `kernel/drivers/serial.c`.
  2. Implémentez `serial_init()` et `serial_putc()`.
  3. Modifiez `kernel/main.c` pour initialiser le pilote.

---

## **🗺️ 5. Roadmap**

### **Objectifs à court terme (0-3 mois)**
| Tâche | Priorité | Statut |
|-------|----------|--------|
| Support du clavier PS/2 | ⭐⭐⭐ | En cours |
| Gestion basique de la mémoire (PMM) | ⭐⭐⭐ | À faire |
| Système de fichiers simplifié (FAT16) | ⭐⭐ | Planifié |
| Documentation complète (API, architecture) | ⭐⭐⭐ | En cours |

### **Objectifs à moyen terme (3-6 mois)**
- **Multitâche coopératif** : Basculer entre tâches via `task_switch()`.
- **Gestion des exceptions** : Handler les `GPF` (General Protection Fault).
- **Shell minimal** : Interpréteur de commandes basique.

### **Objectifs à long terme (6+ mois)**
- **Système de fichiers journalisé** (ext2-like).
- **Pilotes pour disques IDE/SATA**.
- **Port vers x86_64** (mode long).

### **Comment proposer une feature ?**
1. Ouvrez une **issue** sur le dépôt pour discuter de la faisabilité.
2. Assignez-vous la tâche si elle est validée.
3. Implémentez-la en suivant les bonnes pratiques.

---

## **📚 Ressources Utiles**
- **Références** :
  - [OSDev Wiki](https://wiki.osdev.org/) (indispensable).
  - *Intel® 64 and IA-32 Architectures Software Developer’s Manual*.
  - *The Linux Kernel Development* (Robert Love) pour les concepts avancés.
- **Outils** :
  - `objdump -d kernel.elf` : Désassemblage du noyau.
  - `readelf -a kernel.elf` : Informations sur le

---
*MaxOS AI v18.0*
