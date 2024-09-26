PROJECT_NAME := $(shell basename $(PWD))
VENV_PATH = ~/.venv/$(PROJECT_NAME)

SRC_DIR := original-gpx
DEST_DIR := simplified-gpx
LOG_DIR := log

FILES := $(wildcard $(SRC_DIR)/*.gpx)
TARGETS := $(FILES:$(SRC_DIR)/%=$(DEST_DIR)/%)

all: venv install jupyter $(TARGETS)

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@source $(VENV_PATH)/bin/activate && \
	pip install --disable-pip-version-check -q -r requirements.txt

jupyter: install
	@source $(VENV_PATH)/bin/activate && \
	python3 -m ipykernel install \
	--user \
	--name "$(PROJECT_NAME)" \
	--display-name "$(PROJECT_NAME)" \
	> /dev/null 2>&1

$(DEST_DIR)/%.gpx: $(SRC_DIR)/%.gpx
	@source $(VENV_PATH)/bin/activate && \
	cat $< | \
	python3 scripts/simplify.py $@ | \
	python3 scripts/format-xml.py > $@; \

clean:
	rm -f $(DEST_DIR)/*
	rm -rf $(LOG_DIR)/*

.PHONY: venv install jupyter