# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

```markdown
# **MaxOS – Documentation Technique (Prototype Bare Metal)**
*Version: 0.1-alpha | Statut: Boot x86 + VGA Texte 80x25*
*Fichiers: 50 (C) + 14 (ASM) | Score: 35/100*

---
## **1. Introduction**
MaxOS est un système d'exploitation **bare metal** en développement pour architecture **x86**, actuellement capable de :
- **Booter en mode réel** (16-bit) via BIOS.
- **Afficher du texte en mode VGA** (80x25, 16 couleurs).
- **Gérer les interruptions basiques** (clavier, timer).

> ⚠️ **Avertissement** : Ce prototype est **expérimental**. Aucune stabilité ou sécurité n'est garantie.

---
## **2. Prérequis**
### **2.1. Outils nécessaires**
| Outil          | Version       | Rôle                          | Lien                                                                 |
|----------------|---------------|-------------------------------|----------------------------------------------------------------------|
| **GCC**        | ≥ 10.0        | Compilation croisée (i686-elf) | [GNU GCC](https://gcc.gnu.org/)                                    |
| **NASM**       | ≥ 2.15        | Assemblage (bootsector)       | [NASM](https://www.nasm.us/)                                       |
| **QEMU**       | ≥ 6.0         | Émulation x86                 | [QEMU](https://www.qemu.org/)                                      |
| **Make**       | ≥ 4.0         | Automatisation des builds     | [GNU Make](https://www.gnu.org/software/make/)                     |
| **GDB**        | ≥ 9.0         | Débogage (optionnel)          | [GDB](https://www.gnu.org/software/gdb/)                           |

### **2.2. Configuration recommandée**
- **OS hôte** : Linux (Ubuntu 22.04+) ou macOS (via Homebrew).
- **Architecture cible** : `i686-elf` (32-bit).
- **Mémoire** : 512 Mo minimum pour QEMU.

---
## **3. Compilation**
### **3.1. Cloner le dépôt**
```bash
git clone https://github.com/votre-utilisateur/MaxOS.git
cd MaxOS
```

### **3.2. Compiler le bootsector (ASM)**
Le bootsector (`boot/boot.asm`) est écrit en NASM et génère un binaire de **512 octets** (secteur de boot standard).
```bash
nasm -f bin boot/boot.asm -o build/boot.bin
```

### **3.3. Compiler le noyau (C)**
Le noyau (`kernel/`) est compilé en **32-bit** avec GCC et lié avec `kernel.ld`.
```bash
# Compiler les sources C en objets
i686-elf-gcc -m32 -ffreestanding -c kernel/kernel.c -o build/kernel.o

# Lier avec le script de linkage
i686-elf-ld -o build/kernel.bin -T kernel/kernel.ld build/kernel.o --oformat binary
```

### **3.4. Créer l'image disque**
Le script `build.sh` automatise la création d'une image disque (`maxos.img`) de **1.44 Mo** (format disquette).
```bash
chmod +x build.sh
./build.sh
```
> **Sortie** : `build/maxos.img` (prêt pour QEMU).

---
## **4. Test avec QEMU**
### **4.1. Lancer l'émulation**
```bash
qemu-system-x86_64 -drive format=raw,file=build/maxos.img
```
**Options utiles** :
| Option                  | Description                                  |
|-------------------------|----------------------------------------------|
| `-d int`                | Afficher les interruptions (débogage).       |
| `-no-reboot`            | Désactiver le redémarrage automatique.      |
| `-serial stdio`         | Rediriger la sortie série vers le terminal. |

### **4.2. Débogage avec GDB**
1. Lancer QEMU en mode débogage :
   ```bash
   qemu-system-x86_64 -drive format=raw,file=build/maxos.img -s -S
   ```
2. Dans un autre terminal, attacher GDB :
   ```bash
   i686-elf-gdb -ex "target remote localhost:1234" -ex "symbol-file build/kernel.bin"
   ```
   **Commandes GDB utiles** :
   - `break *0x7C00` : Point d'arrêt sur le bootsector.
   - `layout src` : Afficher le code source.
   - `info registers` : Lister les registres.

---
## **5. Structure des Fichiers**
```
MaxOS/
├── boot/
│   ├── boot.asm          # Bootsector (16-bit, mode réel)
│   └── gdt.asm           # Définition de la GDT (passage en 32-bit)
├── kernel/
│   ├── kernel.c          # Point d'entrée du noyau (32-bit)
│   ├── vga.c             # Gestion de l'affichage VGA
│   ├── idt.c             # Gestion des interruptions (IDT)
│   ├── keyboard.c        # Driver clavier (IRQ1)
│   └── kernel.ld         # Script de linkage
├── build/                # Binaires générés
├── build.sh              # Script de build
└── README.md             # Documentation
```

---
## **6. Contribuer au Projet**
### **6.1. Rapporter un bug**
- Ouvrir une **issue** sur GitHub avec :
  - **Titre clair** (ex: `[BUG] Échec du boot sur QEMU 7.0`).
  - **Étapes pour reproduire**.
  - **Logs** (sortie de QEMU avec `-d int`).

### **6.2. Soumettre une pull request (PR)**
1. Forker le dépôt.
2. Créer une branche :
   ```bash
   git checkout -b feature/nom-de-la-feature
   ```
3. Respecter les **conventions** :
   - **C** : Norme **K&R** (indentation 4 espaces).
   - **ASM** : Commentaires NASM (`; Commentaire`).
   - **Commits** : Messages en anglais, format `type(scope): description`.
     Ex: `feat(vga): add color support for text`.
4. Pousser et ouvrir une PR vers `main`.

### **6.3. Priorités de développement**
| Tâche                  | Difficulté | Statut      |
|------------------------|------------|-------------|
| Passage en mode 32-bit | Moyenne    | ✅ Done     |
| Gestion mémoire basique| Élevée     | ❌ TODO     |
| Système de fichiers    | Très élevée| ❌ Backlog  |
| Multitâche coopératif  | Élevée     | ❌ Backlog  |

---
## **7. Roadmap**
### **7.1. Version 0.2 (Q1 2025)**
- **Objectifs** :
  - Support du **mode protégé 32-bit** (GDT/IDT fonctionnelles).
  - Allocateur mémoire basique (`kmalloc`).
  - Driver clavier complet (gestion des touches spéciales).
- **Metrics** :
  - Score : **60/100**.
  - Fichiers : **~80 (C/ASM)**.

### **7.2. Version 0.3 (Q2 2025)**
- **Objectifs** :
  - Système de fichiers **FAT16** (lecture/écriture).
  - Shell minimal (`maxsh`) avec commandes basiques (`ls`, `cat`).
  - Support des **appels système**.
- **Metrics** :
  - Score : **80/100**.
  - Fichiers : **~120 (C/ASM)**.

### **7.3. Version 1.0 (2026)**
- **Objectifs finaux** :
  - Multitâche préemptif.
  - Réseau (pilote **RTL8139**).
  - Portage sur **RISC-V** (expérimental).

---
## **8. Licence**
MaxOS est distribué sous **licence MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

---
## **9. Contact**
- **Mainteneur** : [Votre Nom](mailto:votre.email@example.com)
- **Communauté** : [Discord/Forum](lien-

---
*MaxOS AI v18.0*
