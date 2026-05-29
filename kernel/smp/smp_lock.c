#include "smp_lock.h"
#include "io.h"

void smp_lock_init(smp_lock_t *lock) {
    lock->lock = 0;
}

void smp_lock_acquire(smp_lock_t *lock) {
    asm volatile(
        "1: lock bts dword [%0], 0\n"
        "   jnc 2f\n"
        "   pause\n"
        "   jmp 1b\n"
        "2:\n"
        : : "r"(&lock->lock) : "memory");
}

void smp_lock_release(smp_lock_t *lock) {
    asm volatile("lock btr dword [%0], 0" : : "r"(&lock->lock) : "memory");
}