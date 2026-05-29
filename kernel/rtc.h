#ifndef RTC_H
#define RTC_H

void rtc_init(void);
unsigned char rtc_read(unsigned char reg);
void rtc_write(unsigned char reg, unsigned char val);
unsigned char rtc_get_update_flag(void);
void rtc_wait_update(void);
void rtc_read_time(unsigned char *hour, unsigned char *min, unsigned char *sec);

#endif