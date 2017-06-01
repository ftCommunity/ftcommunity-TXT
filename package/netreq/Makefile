# sudo apt-get install libnetfilter-queue-dev

PROG=netreq

all: $(PROG)

$(PROG): $(PROG).o
	$(CC) -o $@ $< -lnetfilter_queue

%.o: %.c 
	$(CC) -o $@ -c $<

clean:
	rm -f $(PROG) *.o *~

install: $(PROG)
	cp $< /usr/bin
