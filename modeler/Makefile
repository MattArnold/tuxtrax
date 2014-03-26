CC=g++
CFLAGS=-c -Wall -fexceptions -std=c++0x -O2
LDFLAGS=-s -lsoci_core -lsoci_sqlite3 -lsoci_postgresql
EXECUTABLE=bin/modeler
SOCI_INC_DIR=soci-3.2.2
POSTGRES_INC_DIR=/usr/include/postgresql
SOCI_LIB_DIR=soci-3.2.2/build/lib
OBJ_DIR=obj
OBJECTS=$(OBJ_DIR)/database.o $(OBJ_DIR)/main.o

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
		$(CC) -L$(SOCI_LIB_DIR) -o $@ $(OBJECTS) $(LDFLAGS)

clean:
	rm -rf $(OBJECTS) $(EXECUTABLE)

$(OBJ_DIR)/%.o: %.cpp
	$(CC) $(CFLAGS) -I$(SOCI_INC_DIR)/core -I$(SOCI_INC_DIR)/backends/postgresql -I$(SOCI_INC_DIR)/backends/sqlite3 -I$(POSTGRES_INC_DIR) $< -o $@