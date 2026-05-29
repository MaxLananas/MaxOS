#include "rtc.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

#define RTC_PORT 0x70
#define RTC_DATA 0x71

void rtc_init(void) {
    outb(RTC_PORT, 0x8A);
    outb(RTC_DATA, 0x20);
    outb(RTC_PORT, 0x8B);
    unsigned char prev = inb(RTC_DATA);
    outb(RTC_PORT, 0x8B);
    outb(RTC_DATA, prev | 0x40);
    screen_writeln("RTC initialized", 0x0A);
}

unsigned char rtc_read(unsigned char reg) {
    outb(RTC_PORT, reg);
    return inb(RTC_DATA);
}

void rtc_write(unsigned char reg, unsigned char val) {
    outb(RTC_PORT, reg);
    outb(RTC_DATA, val);
}

unsigned char rtc_get_update_flag(void) {
    outb(RTC_PORT, 0x0C);
    return inb(RTC_DATA);
}

void rtc_wait_update(void) {
    while (rtc_get_update_flag() & 0x10);
}

void rtc_read_time(unsigned char *hour, unsigned char *min, unsigned char *sec) {
    rtc_wait_update();
    *sec = rtc_read(0x00);
    *min = rtc_read(0x02);
    *hour = rtc_read(0x04);
}