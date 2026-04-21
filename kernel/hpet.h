#ifndef HPET_H
#define HPET_H

int hpet_init(void);
unsigned long long hpet_get_ticks(void);
void hpet_sleep(unsigned int ms);

#endif