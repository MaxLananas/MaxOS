unsigned short* vga_buffer;
unsigned int cursor_pos;

void screen_init() {
    vga_buffer=(unsigned short*)0xB8000;
    for(unsigned int i=0;i<80*25;i++) {
        vga_buffer[i]=(0x0F<<8)|' ';
    }
    cursor_pos=0;
}

void screen_write(const char* str,unsigned int len) {
    for(unsigned int i=0;i<len;i++) {
        if(cursor_pos>=80*25) {
            cursor_pos=0;
        }
        vga_buffer[cursor_pos++]=(0x0F<<8)|str[i];
    }
}

void screen_write_hex(unsigned int num) {
    const char hex_chars[]="0123456789ABCDEF";
    char buffer[9];
    buffer[8]=0;

    for(int i=7;i>=0;i--) {
        buffer[i]=hex_chars[num&0xF];
        num>>=4;
    }

    screen_write(buffer,8);
}