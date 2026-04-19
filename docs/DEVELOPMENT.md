# Guide de développement MaxOS

## Environnement requis
- GCC (version supportant -m32)
- NASM
- LD (GNU Linker)
- QEMU (pour le test)
- Make

## Compilation
```bash
make        # Compile le système
make run    # Lance QEMU avec l'OS
make clean  # Nettoie les fichiers de build
```

## Règles de codage strictes

### Interdits absolus
- Aucune inclusion de fichiers de la libc standard
- Pas de fonctions de la libc (malloc, printf, etc.)
- Pas de types standard (size_t, bool, etc.)
- Pas de macros répétitives pour les ISR

### Remplacements obligatoires
| Élément interdit | Remplacement |
|------------------|--------------|
| stddef.h         | Utiliser unsigned int |
| string.h         | Implémenter manuellement |
| stdlib.h         | Éviter toute allocation dynamique |
| stdio.h          | Utiliser des fonctions bas niveau |
| size_t           | unsigned int |
| bool/true/false  | int/1/0 |
| uint32_t         | unsigned int |
| uint8_t          | unsigned char |
| uint16_t         | unsigned short |

### Organisation des fichiers
1. Chaque .c doit avoir un .h correspondant
2. Les includes doivent utiliser des chemins relatifs à la racine
3. Les nouveaux .c doivent être ajoutés dans le Makefile OBJS
4. Pas de commentaires dans le code généré

## Structure du projet
```
MaxOS/
├── boot/           # Bootloader
├── kernel/         # Code noyau
├── drivers/        # Pilotes
├── apps/           # Applications
├── ui/             # Interface utilisateur
├── docs/           # Documentation
├── tests/          # Tests unitaires
├── Makefile        # Règles de build
└── linker.ld       # Script de linkage
```

## Bonnes pratiques
1. Tester chaque module indépendamment
2. Vérifier la taille du kernel après chaque modification
3. Utiliser QEMU en mode nographic pour le débogage
4. Documenter toute nouvelle fonctionnalité
5. Respecter les conventions de nommage

## Débogage
```bash
make run-nographic  # Mode console
# Dans QEMU:
# Ctrl+A puis C pour entrer dans le moniteur
# info registers pour voir les registres
```

## Contraintes techniques
- Le kernel doit tenir dans 2879 secteurs (1,44 Mo)
- Pas de position independent code (PIC)
- Mode 32 bits uniquement
- Pas de protection mémoire

## Workflow recommandé
1. Implémenter une nouvelle fonctionnalité
2. Ajouter des tests unitaires
3. Documenter dans ARCHITECTURE.md si nécessaire
4. Vérifier que le build passe
5. Tester dans QEMU
6. Nettoyer le code avant commit