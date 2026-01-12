# Contributing to A.B.E.L.

Merci de contribuer à A.B.E.L. ! Ce document explique comment participer au projet.

## Code of Conduct

En participant, vous acceptez de respecter notre code de conduite.

## Comment Contribuer

### Reporter un Bug

1. Vérifiez que le bug n'a pas déjà été reporté
2. Créez une issue avec le template "Bug Report"
3. Incluez les étapes pour reproduire le problème

### Proposer une Feature

1. Créez une issue avec le template "Feature Request"
2. Décrivez le cas d'usage et les bénéfices
3. Attendez la validation avant de commencer le développement

### Pull Requests

1. Fork le repository
2. Créez une branche feature (`git checkout -b feature/ma-feature`)
3. Committez vos changements (`git commit -m 'Add: ma feature'`)
4. Push vers la branche (`git push origin feature/ma-feature`)
5. Ouvrez une Pull Request

## Standards de Code

### Backend (Python)

- Suivre PEP 8
- Type hints obligatoires
- Docstrings pour les fonctions publiques
- Tests unitaires pour les nouvelles features

```bash
# Linting
ruff check .
mypy app

# Tests
pytest
```

### Mobile (TypeScript)

- ESLint + Prettier
- Types stricts (no `any`)
- Composants fonctionnels avec hooks

```bash
# Linting
npm run lint

# Type check
npx tsc --noEmit
```

## Sécurité

- **JAMAIS** de secrets dans le code
- Validation de toutes les entrées utilisateur
- Pas de `console.log` en production
- Revue de sécurité pour les PRs touchant à l'auth

## Questions

Ouvrez une Discussion GitHub pour toute question.
