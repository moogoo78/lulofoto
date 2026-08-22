# lulofoto - import photos, then open the destination in the file manager

PYTHON := $(shell [ -x .venv/bin/python3 ] && echo .venv/bin/python3 || echo python3)
CONFIG := $(HOME)/.lulofoto_config.json
OPEN := xdg-open

# Destination directory from the saved config, falling back to ./fotos
DEST = $(shell $(PYTHON) -c "import json,os;print(json.load(open(os.path.expanduser('$(CONFIG)'))).get('destination') or 'fotos')" 2>/dev/null || echo fotos)

.PHONY: all run open clean

all: run open

run:
	$(PYTHON) ./lulofoto.py $(ARGS)

open:
	@echo "Opening $(DEST) ..."
	@$(OPEN) "$(DEST)" >/dev/null 2>&1 &

clean:
	rm -rf __pycache__
