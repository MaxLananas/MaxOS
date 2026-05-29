#include "hpet.h"
#include "idt.h"
#include "irq.h"
#include "screen.h"

#define HPET_BASE 0xFED00000
#define HPET_ID (HPET_BASE + 0x000)
#define HPET_CONFIG (HPET_BASE + 0x010)
#define HPET_COUNTER (HPET_BASE + 0x0F0)
#define HPET_TIMER0 (HPET_BASE + 0x100)

typedef struct {
    unsigned int cap_id;
    unsigned int period;
} hpet_info_t;

static hpet_info_t hpet_info;

void hpet_init(void) {
    unsigned int id = inl(HPET_ID);
    hpet_info.cap_id = id;
    hpet_info.period = (id >> 32) & 0xFFFFFFFF;

    outl(HPET_CONFIG, 0x01);
    outl(HPET_COUNTER, 0);
    screen_writeln("HPET initialized", 0x0A);
}

unsigned long long hpet_get_ns(void) {
    unsigned long long counter = inl(HPET_COUNTER);
    return counter * hpet_info.period;
}

void hpet_sleep_ns(unsigned long long ns) {
    unsigned long long start = hpet_get_ns();
    while ((hpet_get_ns() - start) < ns);
}