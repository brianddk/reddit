// gcc -o bcmticks bcmticks.c -lbcm_host && sudo ./bcmticks

// [rights]  Copyright 2023 brianddk at github https://github.com/brianddk
// [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
// [repo]    github.com/brianddk/reddit/blob/master/c/bcmticks.c
// [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
// [tipjar]  github.com/brianddk/reddit/blob/master/tipjar/tipjar.txt
// [req]     apt-get install libraspberrypi-dev
// [note]    This will pull processor ticks off the ARM timer on BCM2835 and 
// [note]      later processors.  It requires sudo, and if run with '-e' it 
// [note]      will write to mapped memory (DANGER!!!).  Enjoy :-)

#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <locale.h>

// libraspberrypi-dev; https://github.com/raspberrypi/userland
#include <bcm_host.h>

// (web archived) https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#peripheral-addresses
#define BCM_PERI_BASE        bcm_host_get_peripheral_address()

#define SYS_TIMER_OFFSET     0x00003000
#define SYS_TIMER_SIZE       0x1C
#define SYS_TIMER_CLO        0x04

#define ARM_TIMER_OFFSET     0x0000B000
#define ARM_TIMER_SIZE       0x424
#define ARM_TIMER_COUNTER    0x420
#define ARM_TIMER_CONTROL    0x408
#define ARM_TIMER_COUNTER_EN 0x00000280

#define ONE_SEC_IN_US        1000000

volatile uint32_t* sys_timer;
volatile uint32_t* arm_timer;

int main(int argc, char *argv[]) {
    // Open /dev/mem to access physical memory
  int cnt_i = ARM_TIMER_COUNTER / 4;
  int ctl_i = ARM_TIMER_CONTROL / 4;
  int clo_i = SYS_TIMER_CLO / 4;
  
  uint32_t clo, cnt, ctrl, start;
  
  int mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
  if (mem_fd == -1) {
      perror("Unable to open /dev/mem");
      return 1;
  }

  // Map the ARM Timer's registers into memory
  arm_timer = (volatile uint32_t*)mmap(NULL, ARM_TIMER_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, mem_fd, BCM_PERI_BASE + ARM_TIMER_OFFSET);
  if (arm_timer == MAP_FAILED) {
      perror("mmap");
      close(mem_fd);
      return 2;
  }

  // Map the System Timer's registers into memory
  sys_timer = (volatile uint32_t*)mmap(NULL, SYS_TIMER_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, mem_fd, BCM_PERI_BASE + SYS_TIMER_OFFSET);
  if (sys_timer == MAP_FAILED) {
      perror("mmap");
      close(mem_fd);
      return 3;
  }

  // Enable ARM Timer counter
  if (ARM_TIMER_COUNTER_EN != (arm_timer[ctl_i] & ARM_TIMER_COUNTER_EN)) {
    if (argc > 1 && strcmp(argv[1], "-e") == 0) {
      arm_timer[ctl_i] = ARM_TIMER_COUNTER_EN;
    }
    else {
      printf("ERROR: Run with '-e' argument as sudo to turn on the ARM counter\n");
      printf("DEBUG: 0x%x\n", arm_timer[ctl_i]);
      return 4;
    }
  }
  
  clo = sys_timer[clo_i];
  if ((clo + 2 * ONE_SEC_IN_US) > UINT32_MAX) {
    printf("ERROR: SYS_TIMER is too high, try again later\n");
    return 5;
  }
    
  cnt = arm_timer[cnt_i];
  if (cnt > 3994967296) { // 2**32 - 300 * 1_000_000
    printf("ERROR: ARM_TIMER is too high, try again later\n");
    return 6;    
  }
    
  start = arm_timer[cnt_i];
  while (sys_timer[clo_i] < clo + ONE_SEC_IN_US) {};
  cnt = arm_timer[cnt_i];
  
  setlocale(LC_NUMERIC, "");
  printf("Received %'u ticks over one second\n", cnt-start);
  
  // Close /dev/mem and unmap memory
  close(mem_fd);
  munmap((void*)arm_timer, ARM_TIMER_SIZE);
  munmap((void*)sys_timer, SYS_TIMER_SIZE);

  return 0;
}
