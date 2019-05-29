#include <stdio.h>
#include <unistd.h>
#include <string.h>


int c_dump(unsigned int sps, unsigned int nsps, unsigned int sleep){

	FILE *f;
	unsigned int conf[3]={sps,nsps,sleep};//sps, nsps, sleep time

	f=fopen("/home/pi/smartsensor/adc_source/conf","wb+");
	fwrite(conf,sizeof(unsigned int), 3,f);
	fclose(f);

	return 0;
}
