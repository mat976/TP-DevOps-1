# Changelog

## [1.0.0] - 2025-10-14
### Added
- Endpoint **/articles** (retourne 200, payload vide).
- Tests Pytest pour vérifier **/articles → 200**.
- CI GitHub Actions: backend tests, install frontend, build Docker images.

### Changed
- Démarrage FastAPI + CORS.
- Initialisation DB rendue tolérante aux erreurs en CI.

### Fixed
- Échecs de tests en CI quand la DB n’est pas disponible.

## [Unreleased]
- (À compléter pour la prochaine version)
