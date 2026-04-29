#ifndef TIMER_H
#define TIMER_H

void timer_init(unsigned int hz);
unsigned int timer_get_ticks(void);
void timer_sleep(unsigned int ms);

#endif