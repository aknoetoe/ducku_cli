"""German word lists."""

GENERIC_TOKENS = {
    # user / users
    "benutzer", "nutzer", "anwender",
    # profile
    "profil",
    # settings
    "einstellungen", "einstellung",
    # config
    "konfiguration", "konfig",
    # data
    "daten",
    # list
    "liste",
    # item / items
    "element", "elemente", "eintrag", "eintraege", "einträge",
    # get / set / create / update / delete / add / remove
    "abrufen", "holen", "erhalten",
    "setzen", "festlegen",
    "erstellen", "anlegen", "erzeugen",
    "aktualisieren", "aendern", "ändern",
    "loeschen", "löschen", "entfernen",
    "hinzufuegen", "hinzufügen", "einfuegen", "einfügen",
    # default
    "standard", "voreinstellung",
    # script
    "skript",
}

CONTENT_CHECK_KEYWORDS = {
    "ci_cd": [
        "pipeline", "kontinuierliche integration", "kontinuierliche bereitstellung",
        "build-pipeline", "automatisierte tests", "deployment-pipeline",
    ],
    "docker": [
        "container", "containerisierung", "abbild", "docker-abbild",
    ],
    "kubernetes": [
        "bereitstellung", "dienst",
    ],
    "serverless": [
        "serverlos", "funktion", "lambda-funktion",
    ],
    "terraform": [
        "infrastruktur", "infrastruktur als code",
    ],
    "makefile": [
        "build", "kompilieren", "build-system",
    ],
    "precommit": [
        "git-hook", "commit-hook",
    ],
    "renovate": [
        "abhängigkeitsaktualisierung", "automatische aktualisierung",
    ],
    "dependabot": [
        "abhängigkeitsaktualisierung", "automatische aktualisierung",
    ],
    "helm": [
        "helm-chart", "kubernetes-paket",
    ],
    "ansible": [
        "playbook", "automatisierung", "konfigurationsverwaltung",
    ],
    "vagrant": [
        "virtuelle maschine",
    ],
    "tox": [
        "testautomatisierung", "virtuelle umgebung",
    ],
    "nx": [
        "monorepo", "nx-workspace",
    ],
}

MOCK_FILENAME_PATTERNS = [
    "hallo", "meine_", "pfad_zu", "meinedatei", "ihredatei",
]

MOCK_DIR_PATTERNS = [
    "/irgendein-verzeichnis/", "/irgendeinverzeichnis/",
    "/beispiel-verzeichnis/", "/beispielverzeichnis/",
]

MOCK_PATH_PATTERNS = [
    "/beispiel.py", "/beispiel.js", "/beispiel.ts",
    "/muster.py", "/muster.js", "/muster.ts",
]
