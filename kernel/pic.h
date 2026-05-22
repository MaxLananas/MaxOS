#ifndef PIC_H
#define PIC_H

void pic_init(void);
void pic_send_eoi(unsigned char irq);

#endif