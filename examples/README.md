# Exemples

Chaque fichier montre un seul sujet, avec du code court et lisible : exemple réalisé à l'iade de l'IA afin d'accelerer le processus : tous ont été verifiés par un humain. Pour le moindre soucis : me contacter via discord : levraiberet

## Lancement

1. Mettre un token discord (bot et non user)

2. Lancer un exemple:

```bash
python examples/01_minimal.py
```

## Liste des exemples

- `01_minimal.py`: bouton unique + reponse simple
- `02_buttons_routing.py`: plusieurs boutons + routing par `custom_id`
- `03_selects.py`: string select + user select
- `04_modales_modernes.py`: modale moderne avec `Label` + radio/checkbox natifs
- `07_modales_variantes.py`: plusieurs modales (text input, select, radio group, checkbox group, checkbox)
- `08_modale_file_upload.py`: modale avec `FileUpload` (type 19)
- `09_components_ops_pages.py`: update/remove/row_update en pratique avec toggle on/off + pages + versions container V2 + tests button-only + disable-all cible par message
- `16_allowed_mentions_and_disable_timeout.py`: allowed mentions style Discord.js (`parse`) + disable auto d'un container via `message_id` apres X secondes
- `17_fast_mode.py`: mode allege pour coder vite (quick container + quick button + routeur de boutons)
- `05_containers_v2.py`: message en container V2
- `06_signed_custom_ids.py`: `custom_id` signe avec validation

## Parcours conseille

1. `01_minimal.py`
2. `03_selects.py`
3. `04_modales_modernes.py`
4. `07_modales_variantes.py`
5. `08_modale_file_upload.py`
6. `09_components_ops_pages.py`
7. `05_containers_v2.py`
