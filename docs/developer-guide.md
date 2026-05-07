# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée selon vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste en 32 bits*

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental conçu pour apprendre les bases des OS modernes. Il inclut :
- Un **bootloader** en ASM (`boot.asm`)
- Un **kernel** chargé à l'adresse `0x1000:0x0000`
- Un passage en **mode 32 bits**
- Une **IDT** initialisée (fichiers `idt.c`/`idt.h`)
- Des **ISR manuels** (sans macros, `isr.asm`)
- Une **configuration des IRQ et du PIC** (`irq.asm`/`irq.c`)
- Un **gestionnaire d'exceptions** (`exceptions.c`)
- Un **gestionnaire de fautes** (`fault_handler.c`)

**Statistiques** :
- **51 fichiers C** | **16 fichiers ASM**
- **Score : 35/100** (Niveau : *desc*)

---

## **🛠️ Guide Développeur**

### **1️⃣ Compilation**
#### **Prérequis**
- **GCC** (pour la compilation C)
- **NASM** (pour l'assemblage)
- **QEMU** (pour l'émulation)
- **Make** (pour automatiser la build)

#### **Étapes**
1. **Cloner le dépôt** (si applicable) :
   ```bash
   git clone https://github.com/votre-utilisateur/MaxOS.git
   cd MaxOS
   ```

2. **Compiler le bootloader et le kernel** :
   ```bash
   make
   ```
   - **Sortie** : Un fichier `kernel.bin` (format binaire brut).

3. **Générer une image disque** (optionnel) :
   ```bash
   make disk
   ```
   - **Sortie** : `maxos.img` (pour QEMU ou un vrai disque).

---

### **2️⃣ Test dans QEMU**
#### **Lancement de base**
```bash
make run
```
- **Options QEMU** :
  - `-fda maxos.img` : Utilise l'image disque.
  - `-serial stdio` : Affiche la sortie série dans le terminal.
  - `-d int` : Active les logs des interruptions (utile pour le débogage).

#### **Débogage avancé**
1. **Lancer QEMU avec GDB** :
   ```bash
   make debug
   ```
   - **Dans un autre terminal** :
     ```bash
     gdb -q kernel.bin
     (gdb) target remote localhost:1234
     (gdb) continue
     ```

2. **Vérifier les logs** :
   - Utilisez `dmesg` ou `serial` pour afficher les messages du kernel.

---

### **3️⃣ Structure des Fichiers**
```
MaxOS/
├── boot/               # Code du bootloader
│   ├── boot.asm        # Chargeur principal (charge le kernel)
│   └── boot_sect.bin   # Secteur de boot (512 octets)
├── kernel/             # Code du kernel
│   ├── arch/           # Architecture spécifique (x86)
│   │   ├── asm/        # Code assembleur
│   │   │   ├── isr.asm  # Gestionnaires d'interruptions (ISR)
│   │   │   ├── irq.asm  # Configuration du PIC et des IRQ
│   │   │   └── ...
│   │   ├── c/          # Code C
│   │   │   ├── idt.c    # Initialisation de l'IDT
│   │   │   ├── irq.c    # Gestion des IRQ
│   │   │   ├── exceptions.c  # Gestion des exceptions
│   │   │   ├── fault_handler.c  # Gestion des fautes
│   │   │   └── ...
│   │   └── include/    # En-têtes
│   │       ├── idt.h
│   │       ├── isr.h
│   │       └── ...
│   ├── drivers/        # Pilotes matériels
│   ├── lib/            # Bibliothèques utilitaires
│   └── main.c          # Point d'entrée du kernel
├── Makefile            # Script de compilation
├── linker.ld           # Script de linkage (pour le kernel)
└── README.md           # Documentation de base
```

#### **Fichiers Clés**
| Fichier          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `boot.asm`       | Charge le kernel à `0x1000:0x0000` et active le mode 32 bits.               |
| `isr.asm`        | Gestionnaires d'interruptions (ISR) sans macros.                            |
| `irq.asm`        | Configuration du PIC (8259) et des IRQ.                                    |
| `idt.c`          | Initialisation de la table des descripteurs d'interruptions (IDT).         |
| `exceptions.c`   | Gestion des exceptions (ex: division par zéro).                            |
| `fault_handler.c`| Gestion des fautes (ex: page fault).                                       |

---

### **4️⃣ Contribuer**
#### **Processus**
1. **Forker le dépôt** et créer une branche :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```

2. **Implémenter votre code** en suivant les conventions :
   - **C** : Respecter le style (indentation, noms de variables).
   - **ASM** : Commenter chaque section critique.
   - **Documenter** les nouvelles fonctions dans les en-têtes.

3. **Tester** :
   - Vérifiez que le kernel compile (`make`).
   - Testez dans QEMU (`make run`).

4. **Soumettre une Pull Request** :
   - Décrivez clairement les changements.
   - Incluez des logs ou captures d'écran si pertinent.

#### **Bonnes Pratiques**
- **Éviter les dépendances externes** (MaxOS est minimaliste).
- **Optimiser pour la lisibilité** (le code est éducatif).
- **Documenter les choix techniques** dans les commentaires.

---

### **5️⃣ Roadmap**
#### **Objectifs à Court Terme (0-6 mois)**
| Tâche                          | Priorité | Statut       |
|--------------------------------|----------|--------------|
| Ajouter un système de fichiers | ⭐⭐⭐⭐   | En cours     |
| Implémenter la pagination      | ⭐⭐⭐    | Planifié     |
| Support du clavier (PS/2)      | ⭐⭐⭐⭐   | À faire      |
| Gestion basique de la mémoire  | ⭐⭐⭐⭐   | En cours     |

#### **Objectifs à Moyen Terme (6-12 mois)**
| Tâche                          | Priorité | Statut       |
|--------------------------------|----------|--------------|
| Multitâche (scheduling)        | ⭐⭐⭐⭐⭐  | Planifié     |
| Pilotes pour le VGA            | ⭐⭐⭐    | À faire      |
| Support des disques (ATA)      | ⭐⭐⭐⭐   | En réflexion |
| Réseau (NE2000)                | ⭐⭐      | À long terme |

#### **Objectifs à Long Terme (12+ mois)**
| Tâche                          | Priorité | Statut       |
|--------------------------------|----------|--------------|
| Portage vers x86_64            | ⭐⭐⭐⭐   | En réflexion |
| Système de paquets             | ⭐⭐      | Idée         |
| Compatibilité avec Linux       | ⭐       | Idée         |

---
## **📜 Licence**
MaxOS est distribué sous la licence **MIT** (voir `LICENSE`).

---
## **🤝 Remerciements**
- Inspiré par **Linux**, **Minix**, et **OSDev Wiki**.
- Merci aux contributeurs open-source pour leurs ressources.

---
**🔗 Liens Utiles**
- [OSDev Wiki](https://wiki.osdev.org/)
- [GNU Assembler (GAS)](https://sourceware.org/binutils/docs/as/)
- [QEMU Documentation](https://www.qemu.org/docs/)

---
*Dernière mise à jour : `date`*
```

---

### **Points

---
*MaxOS AI v18.0*
