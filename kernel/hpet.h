#ifndef HPET_H
#define HPET_H

#include "io.h"

void hpet_init(void);
unsigned long long hpet_get_ns(void);
void hpet_sleep_ns(unsigned long long ns);

#endif