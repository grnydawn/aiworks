PYTHON = python
SRC_DIR = src
TEST_DIR = tests
INPUT_DIR = data
OUTPUT_DIR = output
MAP_FILE = data/map_MPASA_QU20km_to_1440x720_bilinear.nc

.PHONY: all install run test clean

all: install test run

install:
	pip install -r requirements.txt

run:
	export PYTHONPATH=$PYTHONPATH:$(pwd) && $(PYTHON) $(SRC_DIR)/main.py --input_dir $(INPUT_DIR) --map_file $(MAP_FILE) --output_dir $(OUTPUT_DIR)

test:
	export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest $(TEST_DIR)

clean:
	rm -rf $(OUTPUT_DIR)
	rm -rf __pycache__
	rm -rf $(SRC_DIR)/__pycache__
	rm -rf $(TEST_DIR)/__pycache__
