#include "hpet.h"
#include "io.h"

#define HPET_BASE 0xFED00000
#define HPET_ID 0x00
#define HPET_PERIOD 0x04
#define HPET_CONFIG 0x10
#define HPET_COUNTER 0xF0

static volatile unsigned char *hpet = (unsigned char *)HPET_BASE;
static unsigned int hpet_freq = 0;
static unsigned int hpet_available = 0;

int hpet_init(void) {
    unsigned int cap_id = *(unsigned int *)(hpet + HPET_ID);
    if ((cap_id & 0x80000000) == 0) {
        return 0;
    }

    hpet_freq = 1000000000 / *(unsigned int *)(hpet + HPET_PERIOD);
    *(unsigned int *)(hpet + HPET_CONFIG) = 0x01;

    unsigned long long counter = *(unsigned long long *)(hpet + HPET_COUNTER);
    while (*(unsigned long long *)(hpet + HPET_COUNTER) == counter) {
        asm volatile("pause");
    }

    hpet_available = 1;
    return 1;
}

unsigned long long hpet_get_ticks(void) {
    if (!hpet_available) {
        return 0;
    }
    return *(unsigned long long *)(hpet + HPET_COUNTER);
}

void hpet_sleep(unsigned int ms) {
    if (!hpet_available) {
        return;
    }

    unsigned long long start = hpet_get_ticks();
    unsigned long long target = start + (ms * (hpet_freq / 1000));

    while (hpet_get_ticks() < target) {
        asm volatile("pause");
    }
}