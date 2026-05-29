#ifndef SMP_LOCK_H
#define SMP_LOCK_H

typedef struct {
    unsigned int lock;
} smp_lock_t;

void smp_lock_init(smp_lock_t *lock);
void smp_lock_acquire(smp_lock_t *lock);
void smp_lock_release(smp_lock_t *lock);

#endif