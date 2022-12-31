PROG=ft_txt_snd_cat

all: $(PROG)

$(PROG): $(PROG).o
	$(CC) -o $@ $<

%.o: %.c 
	$(CC) -o $@ -c $<

clean:
	rm -f $(PROG) *.o *~

install: $(PROG)
	cp $< /usr/bin
