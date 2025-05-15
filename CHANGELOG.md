## [v0.2.4] - 2025-05-15

### Added
- Fixturage PDF complet (`brief_simple.pdf`, `brief_multi.pdf`)
- Script `publish_ghcr.sh` pour publication automatisée sur GHCR
- Archive `.tar.gz` + hash `SHA256SUM.txt`

### Fixed
- Tests restaurés à 100% verts
- Correction `.gitignore` bloquant les fichiers PDF

### Clean
- Suppression de tous les fichiers `* 2.*` (doublons de dev)
- Nettoyage `.pyc`, `__pycache__`, tests suspendus

### Docker
- Image Docker stable `v0.2.4` buildée et testée localement
- Push réussi sur GHCR : `ghcr.io/namtar-afk/revolver-ai-bot:v0.2.4`

