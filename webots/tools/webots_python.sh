#!/bin/bash
# Обёртка: Webots по умолчанию ищет команду `python`, на macOS обычно есть только `python3`.
# В Webots: Preferences → Python command → полный путь к этому файлу
#   (или сразу /usr/bin/python3).
exec /usr/bin/python3 "$@"
