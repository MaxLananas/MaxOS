#include "nvme.h"
#include "io.h"
#include "screen.h"

#define NVME_BAR0       0xE0000000
#define NVME_CAP        (NVME_BAR0 + 0x00)
#define NVME_VS         (NVME_BAR0 + 0x08)
#define NVME_CC         (NVME_BAR0 + 0x14)
#define NVME_CSTS       (NVME_BAR0 + 0x1C)
#define NVME_AQA        (NVME_BAR0 + 0x24)
#define NVME_ASQ        (NVME_BAR0 + 0x28)
#define NVME_ACQ        (NVME_BAR0 + 0x30)
#define NVME_SQ0TDBL    (NVME_BAR0 + 0x1000)
#define NVME_CQ0HDBL    (NVME_BAR0 + 0x1008)

#define NVME_CMD_READ   0x02
#define NVME_CMD_WRITE  0x01

typedef struct {
    unsigned int dword0;
    unsigned int dword1;
    unsigned int dword2;
    unsigned int dword3;
    unsigned int dword4;
    unsigned int dword5;
    unsigned int dword6;
    unsigned int dword7;
} nvme_command_t;

static void nvme_wait_ready(void) {
    unsigned int timeout = 100000;
    while (timeout--) {
        unsigned int csts = inl(NVME_CSTS);
        if ((csts & 0x1) == 0) {
            break;
        }
    }
}

static void nvme_init_controller(void) {
    nvme_wait_ready();

    unsigned int cap = inl(NVME_CAP);
    unsigned int mps = 1 << (12 + ((cap >> 16) & 0xF));
    unsigned int css = (cap >> 24) & 0xFF;

    outl(NVME_CC, 0x46);
    while ((inl(NVME_CSTS) & 0x1) == 1);
}

void nvme_init(void) {
    nvme_init_controller();
    screen_writeln("NVMe: Controller initialized", 0x02);
}

int nvme_read_blocks(unsigned int lba, unsigned char *buffer, unsigned int count) {
    nvme_command_t cmd;
    cmd.dword0 = (NVME_CMD_READ << 16) | (1 << 14) | (0 << 10);
    cmd.dword1 = lba & 0xFFFFFFFF;
    cmd.dword2 = (lba >> 32) & 0xFFFFFFFF;
    cmd.dword3 = (unsigned int)buffer;
    cmd.dword4 = count;
    cmd.dword5 = 0;
    cmd.dword6 = 0;
    cmd.dword7 = 0;

    for (unsigned int i = 0; i < count; i++) {
        outl(NVME_SQ0TDBL, cmd.dword0);
        while ((inl(NVME_CSTS) & 0x2) == 0);
    }
    return 1;
}

int nvme_write_blocks(unsigned int lba, unsigned char *buffer, unsigned int count) {
    nvme_command_t cmd;
    cmd.dword0 = (NVME_CMD_WRITE << 16) | (1 << 14) | (0 << 10);
    cmd.dword1 = lba & 0xFFFFFFFF;
    cmd.dword2 = (lba >> 32) & 0xFFFFFFFF;
    cmd.dword3 = (unsigned int)buffer;
    cmd.dword4 = count;
    cmd.dword5 = 0;
    cmd.dword6 = 0;
    cmd.dword7 = 0;

    for (unsigned int i = 0; i < count; i++) {
        outl(NVME_SQ0TDBL, cmd.dword0);
        while ((inl(NVME_CSTS) & 0x2) == 0);
    }
    return 1;
}