/*
  txt_snd_cat

  (c) 2016 by Till Harbaum <till@harbaum.org>
 */

#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/types.h>
#include <linux/spi/spidev.h>

// spi setup
#define SPI_DEV   "/dev/spidev1.0"
#define SPI_MODE  (SPI_CPHA | SPI_CPOL)
#define SPI_BITS  8
#define SPI_SPEED 1000000     // buffer reports start to fail at 2mhz
#define SPI_DELAY 0

// command bytes to be sent to SPI client
#define SOUND_CMD_STATUS      0x80
#define SOUND_CMD_DATA        0x81
#define SOUND_CMD_RESET       0x90

// status bytes returned by SPI client
#define SOUND_MSG_RX_CMD      0xBB   // expecting command
#define SOUND_MSG_RX_DATA     0x55   // expecting data
#define SOUND_MSG_RX_COMPLETE 0xAA   // padding of 441 byte data frame
#define SOUND_MSG_ERR_SIZE    0xFE   // cannot happen due to firmware bug
#define SOUND_MSG_ERR_FULL    0xFF   

#ifdef DEBUG
#define debug_putchar(a) putchar(a)
#else
#define debug_putchar(a) ;
#endif

// exchange n bytes via SPI
int spi_n(int fd, uint8_t *tx, uint8_t *rx, int len) {
  int ret;

  struct spi_ioc_transfer tr = {
    .tx_buf = (__u32)tx,
    .rx_buf = (__u32)rx,
    .len = len,
    .delay_usecs = SPI_DELAY,
    .speed_hz = SPI_SPEED,
    .bits_per_word = SPI_BITS,
  };

  if((ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr)) < 0) {
    perror("SPI transfer error");
    return ret;
  }

  return 0;
}

// exchange a single byte via SPI
int spi(int fd, uint8_t tx) {
  uint8_t rx;
  int ret;

  if((ret = spi_n(fd, &tx, &rx, 1)) < 0)
    return ret;

  return 0xff & rx;
}

// send 0 bytes until the SPI client reports to be able to accept commands
int cmd_flush(int fd) {
  int timeout = 512;

  while((spi(fd,0) != SOUND_MSG_RX_CMD) && timeout)
    timeout--;
    
  return timeout;
}

// send a three byte command incl transaction id and size
int send_cmd(int fd, uint8_t cmd, uint8_t size) {
  static uint8_t transaction_id = 0;
  int ret;
  uint8_t rx[3], tx[] = { cmd, transaction_id++, size };

  if((ret = spi_n(fd, tx, rx, 3)) < 0)
    return ret;

  // check if SPI client was expecting a command
  if(rx[0] != SOUND_MSG_RX_CMD) {
    fprintf(stderr, "SPI client wasn't expecting a command\n");
    return -1;
  }

  // check if number of free buffers sounds reasonable
  if(rx[1] > 10) {
    fprintf(stderr, "SPI client returned unexpected number of buffers\n");
    return -1;
  }

  // check if the transaction id has correctly been returned
  if(rx[2] != tx[1]) {
    fprintf(stderr, "SPI client returned unexpected transaction id\n");
    return -1;
  }

  return 0xff & rx[1];
}

int send_chunk(int fd, uint8_t *data, uint8_t len) {
  int ret, buffers;

  // send command
  if((ret = send_cmd(fd, SOUND_CMD_DATA, len)) < 0) {
    fprintf(stderr, "Error sending data command\n");
    return ret;
  }

  // send_cmd returns the number of available buffers
  buffers = ret;

  // send payoad itself
  if((ret = spi_n(fd, data, NULL, len?len:441)) < 0) {
    fprintf(stderr, "Error sending data\n");
    return ret;
  }

  // return number of free buffers. It's actually one less than
  // this since we just sent data and filled one more
  return buffers;
}

// read a given number of bytes
int read_n(int fd, uint8_t *buffer, int len) {
  int cnt = 0;
  
  while(len) {
    int ret = read(fd, buffer, len);
    // error? return it
    if(ret < 0) {
      perror("input read()");
      return ret;
    }
    
    // end of file? return what has been read so far
    if(ret == 0) return cnt;

    cnt += ret;
    buffer += ret;
    len -= ret;
  }

  return cnt;
}

// wait for free buffers in SPI client
int wait4buffers(int fd) {
  int ret;
  
  do {
    debug_putchar('-');

    // sleep 20ms
    usleep(20000);

    // request number of free buffers
    if((ret = send_cmd(fd, SOUND_CMD_STATUS, 0)) < 0) {
      fprintf(stderr, "Unable to read client status\n");
      return ret;
    }
  } while(ret == 1);

  return ret;
}
  
int send_file(int spi_fd, int file_fd) {
  int ret;

  // flush spi device to make sure it accepts commands
  if((ret = cmd_flush(spi_fd)) < 0) {
    fprintf(stderr, "Unable to get SPI client into command mode\n");
    return ret;
  }

  // reset the SPI client
  if((ret = send_cmd(spi_fd, SOUND_CMD_RESET, 0)) < 0) {
    fprintf(stderr, "Unable to reset the SPI client\n");
    return ret;
  }

  // we just opened the connection, so there cannot be any
  // buffers in use. But it doesn't hurt to check ...
  if(!ret)
    wait4buffers(spi_fd);
  
  // read and forward chunks of input data
  while(1) {
    int buffers;
    uint8_t buffer[441];
    int size = read_n(file_fd, buffer, sizeof(buffer));

    // for some odd reason, the 0x90 (SOUND_CMD_RESET) must not appear
    // in the data stream. Otherwise playback goes completely nuts
    int i;
    for(i=0;i<size;i++) 
      if(buffer[i] == 0x90)
	buffer[i] = 0x91;
    
    debug_putchar('.');
    if(size == 441)
      ret = send_chunk(spi_fd, buffer, 0);
    else if(size > 0) {
      // if there isn't enough data for a full frame, then
      // we may have to send two chunks for the rest if less
      // than 441 and more than 255 bytes are to be sent
      if(size > 255) {
	// send first 255 bytes
	if((ret = send_chunk(spi_fd, buffer, 255)) < 0)
	  return ret;
	// we may have to wait for more buffers
	if(ret == 1) ret = wait4buffers(spi_fd);
	// send rest
	ret = send_chunk(spi_fd, buffer+255, size-255);
      } else
	ret = send_chunk(spi_fd, buffer, size);
    } else
      break;   // end on input file eof or read error

#ifdef DEBUG
    fflush(stdout);
#endif

    // bail out on error
    if(ret < 0)
      return ret;
    
    // send_chunk returned the number of buffers _before_ the chunk
    // was sent
    buffers = ret;

    // this should never happen since we should have been waiting for
    // a free buffer before
    if(buffers == 0)
      debug_putchar('X');

    // only one buffer was left before last chunk was sent?
    if(buffers == 1)
      buffers = wait4buffers(spi_fd);
  }

  return 0;
}

int main(int argc, char *argv[]) {
  uint8_t mode = SPI_MODE;
  uint8_t bits = SPI_BITS;
  uint32_t speed = SPI_SPEED;

  int ret = 0;
  int fd;

  if((fd = open(SPI_DEV, O_RDWR)) < 0) {
    perror("can't open device");
    exit(-1);
  }
    
  /*
   * spi mode
   */
  if((ret = ioctl(fd, SPI_IOC_WR_MODE, &mode)) < 0) {
    perror("can't set spi mode");
    close(fd);
    exit(-1);
  }
    
  if((ret = ioctl(fd, SPI_IOC_RD_MODE, &mode)) < 0) {
    perror("can't get spi mode");
    close(fd);
    exit(-1);
  }
  
  /*
   * bits per word
   */
  if(bits) {
    if((ret = ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits)) < 0) {
      perror("can't set bits per word");
      close(fd);
      exit(-1);
    }
  }

  if((ret = ioctl(fd, SPI_IOC_RD_BITS_PER_WORD, &bits)) < 0) {
    perror("can't get bits per word");
    close(fd);
    exit(-1);
  }

  /*
   * max speed hz
   */
  if(speed) {
    if((ret = ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed)) < 0) {
      perror("can't set max speed hz");
      close(fd);
      exit(-1);
    }
  }

  if((ret = ioctl(fd, SPI_IOC_RD_MAX_SPEED_HZ, &speed)) < 0) {
    perror("can't get max speed hz");
    close(fd);
    exit(-1);
  }
  
#ifdef DEBUG  
  printf("spi mode: %d\n", mode);
  printf("bits per word: %d\n", bits);
  printf("max speed: %d Hz\n", speed);
#endif
  
  send_file(fd, 0);

  close(fd);
  
  return ret;
}
