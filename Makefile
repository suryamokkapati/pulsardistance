CC      = gcc
CFLAGS  = -O2 -Wall -Wextra -std=c99
LDFLAGS = -lm

TARGET  = pulsar
SRC     = src/main.c ymw16/ymw16.c

PREFIX  ?= /usr/local
BINDIR  = $(PREFIX)/bin

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -Iymw16 -o $(TARGET) $(SRC) $(LDFLAGS)

install: $(TARGET)
	install -Dm755 $(TARGET) $(DESTDIR)$(BINDIR)/$(TARGET)

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/$(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: install uninstall clean
