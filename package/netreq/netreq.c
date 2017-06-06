// netreq.c - Till Harbaum
//
// preparation
// iptables -A INPUT -i lo -j ACCEPT
// iptables -A INPUT -p tcp -m state --state NEW -j NFQUEUE --queue-num 1
// add exeptions for permanently allowed hosts:
// iptables -I INPUT 1 -m mac --mac-source d4:be:d9:63:7c:c4 -j ACCEPT

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <termios.h>
#include <sys/poll.h>
#include <netinet/in.h>
#include <linux/types.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/netfilter.h>            /* for NF_ACCEPT */

#include <libnetfilter_queue/libnetfilter_queue.h>

// keep a list of devices that are allowed or disabllowed
// to access this machine
typedef struct {
  unsigned char hw_addr[6];
} device_t;

int allowed_len = 0;
device_t *allowed = NULL;
int denied_len = 0;
device_t *denied = NULL;
device_t *pending = NULL;    // pending request

static int verify_pkt (struct nfq_data *tb) {
  struct nfqnl_msg_packet_hdr *ph;
  struct nfqnl_msg_packet_hw *hwph;
  struct iphdr *iph;
  struct tcphdr *tcph;
  
  ph = nfq_get_msg_packet_hdr(tb);
  if(!ph) return -1;

  // check for IP
  if(ntohs(ph->hw_protocol) != 0x800)
    return -1;

  hwph = nfq_get_packet_hw(tb);
  if(!hwph) return -1;

  // only accept 6 byte hw addresses
  // this may fail with USB net. But we don't want to restricht that
  // anyway
  if(ntohs(hwph->hw_addrlen) != 6)
    return -1;

  // the rest are payload checks
  // error or less than ip+tcp headers
  if(nfq_get_payload(tb, (unsigned char **)&iph) < 40)
    return -1;

  // check for valid ipv4 header
  if((iph->version != 4) || (iph->ihl != 5))
    return -1;

  // don't allow fragmentation
  if((ntohs(iph->frag_off) & 0x1fff) != 0)
    return -1;

  // only deal with tcp
  if(iph->protocol != 6)
    return -1;

  // and take a peak into the tcp header
  tcph = (struct tcphdr*)(((char*)iph)+20);

  // ignore anything that doesn't have a syn flag
  if(!tcph->syn)
    return -1;
  
  return 0;
}

int get_info(struct nfq_data *tb, device_t *dev, char *ip_addr, uint16_t *port) {
  struct nfqnl_msg_packet_hw *hwph;
  struct iphdr *iph;
  struct tcphdr *tcph;

  hwph = nfq_get_packet_hw(tb);
  if(!hwph) return -1;
  memcpy(dev->hw_addr, hwph->hw_addr, 6);
  
  if(nfq_get_payload(tb, (unsigned char **)&iph) < 40)
    return -1;
  memcpy(ip_addr, &iph->saddr, 4);
	 
  tcph = (struct tcphdr*)(((char*)iph)+20);
  *port = ntohs(tcph->dest);
  
  return 0;
}

int check_input() {
  struct pollfd fds;
  int ret;
  fds.fd = 0; /* this is STDIN */
  fds.events = POLLIN;
  ret = poll(&fds, 1, 0);
  if(ret == 1)
    return fgetc(stdin);
    
  return 0;
}
  
static int cb(struct nfq_q_handle *qh, struct nfgenmsg *nfmsg,
              struct nfq_data *nfa, void *data) {
  u_int32_t id = 0;
  int d;
  struct nfqnl_msg_packet_hdr *ph;
  ph = nfq_get_msg_packet_hdr(nfa);
  if(ph) id = ntohl(ph->packet_id);

  // verify some basic patterns and drop packet if it's
  // somehow unexpected
  if(verify_pkt(nfa) != 0)
    return nfq_set_verdict(qh, id, NF_DROP, 0, NULL);

  uint8_t ip_addr[4];
  device_t dev;
  uint16_t port;
  if(get_info(nfa, &dev, ip_addr, &port) != 0)
    return nfq_set_verdict(qh, id, NF_DROP, 0, NULL);

  // check if this device already has an entry in the denied/allowed lists
  for(d=0;d<allowed_len;d++) {
    if(memcmp(allowed[d].hw_addr, dev.hw_addr, 6) == 0)
      return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
  }
    
  for(d=0;d<denied_len;d++)
    if(memcmp(denied[d].hw_addr, dev.hw_addr, 6) == 0)
      return nfq_set_verdict(qh, id, NF_DROP, 0, NULL);
  
  // if we have a pending request then just drop everything
  // elso until the current request has been answered
  if(pending)
    return nfq_set_verdict(qh, id, NF_DROP, 0, NULL);
  
  pending = malloc(sizeof(device_t));
  *pending = dev;
       
  printf("REQ ");
  
  // print the info
  int i;
  for (i = 0; i < 5; i++)
    printf("%02x:", pending->hw_addr[i]);
  printf("%02x ", pending->hw_addr[5]);

  for (i = 0; i < 3; i++)
    printf("%u.", ip_addr[i]);
  printf("%u ", ip_addr[3]);

  printf("%u\n", port);

  printf("-> A(ccept), D(eny), I(gnore), Q(uit): ");
  fflush(stdout);
  
  //   return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
  return nfq_set_verdict(qh, id, NF_DROP, 0, NULL);
}

int main(int argc, char **argv) {
  struct nfq_handle *h;
  struct nfq_q_handle *qh;
  struct nfnl_handle *nh;
  struct termios tio, old_tio;
  fd_set readfds;
  int fd;
  int rv;
  int ret;
  char buf[4096] __attribute__ ((aligned));
  int run = 1;
  
  // opening library handle
  h = nfq_open();
  if (!h) {
    fprintf(stderr, "error during nfq_open()\n");
    exit(1);
  }
  
  // unbinding existing nf_queue handler for AF_INET (if any)
  if (nfq_unbind_pf(h, AF_INET) < 0) {
    fprintf(stderr, "error during nfq_unbind_pf()\n");
    exit(1);
  }
  
  // binding nfnetlink_queue as nf_queue handler for AF_INET
  if (nfq_bind_pf(h, AF_INET) < 0) {
    fprintf(stderr, "error during nfq_bind_pf()\n");
    exit(1);
  }
  
  // binding this socket to queue '1'
  qh = nfq_create_queue(h,  1, &cb, NULL);
  if (!qh) {
    fprintf(stderr, "error during nfq_create_queue()\n");
    exit(1);
  }
  
  // setting copy_packet mode
  if (nfq_set_mode(qh, NFQNL_COPY_PACKET, 0xffff) < 0) {
    fprintf(stderr, "can't set packet_copy mode\n");
    exit(1);
  }

  /* get the terminal settings for stdin */
  tcgetattr(STDIN_FILENO, &tio);
  old_tio = tio;
  
  /* disable canonical mode (buffered i/o) and local echo */
  tio.c_lflag &=(~ICANON & ~ECHO);
  
  /* set the new settings immediately */
  tcsetattr(STDIN_FILENO,TCSANOW,&tio);
  
  fd = nfq_fd(h);

  while(run) {
    FD_ZERO(&readfds);
    FD_SET(0, &readfds);
    FD_SET(fd, &readfds);
  
    ret = select( fd + 1, &readfds, NULL, NULL, NULL);
    if(ret >= 0) {
      if(FD_ISSET(0, &readfds)) {
	int ch = fgetc(stdin);

	// q - quit
	if(ch == 'q') {
	  puts("quit");
	  run = 0;
	}
	
	// i - ignore request
	if((ch == 'i') && pending) {
	  puts("ignored");
	  free(pending);
	  pending = NULL;
	}
	
	// a - accept request
	if((ch == 'a') && pending) {
	  puts("accepted");
	  allowed = realloc(allowed, (allowed_len+1) * sizeof(device_t));
	  allowed[allowed_len++] = *pending;
	  free(pending);
	  pending = NULL;
	}

	// d - deny request
	if((ch == 'd') && pending) {
	  puts("denied");
	  denied = realloc(denied, (denied_len+1) * sizeof(device_t));
	  denied[denied_len++] = *pending;
	  free(pending);
	  pending = NULL;
	}
	
	// s - show
	if(ch == 's') {
	  puts("");
	  int d, i;

	  printf("Allowed:\n");
	  for(d=0;d<allowed_len;d++) {
	    for (i = 0; i < 5; i++)
	      printf("%02x:", allowed[d].hw_addr[i]);
	    printf("%02x\n", allowed[d].hw_addr[5]);
	  }
	  
	  printf("Denied:\n");
	  for(d=0;d<denied_len;d++) {
	    for (i = 0; i < 5; i++)
	      printf("%02x:", denied[d].hw_addr[i]);
	    printf("%02x\n", denied[d].hw_addr[5]);
	  }
	}
      }
      if(FD_ISSET(fd, &readfds)) {
	rv = recv(fd, buf, sizeof(buf), 0);
	nfq_handle_packet(h, buf, rv);
      }
    }
  }
      
  nfq_destroy_queue(qh);
  
  nfq_close(h);

  /* restore the former settings */
  tcsetattr(STDIN_FILENO,TCSANOW,&old_tio);
  
  exit(0);
}
