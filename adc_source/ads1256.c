#include "ads1256.h"

/// custom code 

#define POWERPIN RPI_GPIO_P1_07 //P7 pin za paljenje i gasenje

//[us] vrijeme potrebno da se npajanje kruga dosegne nominalni napon i ustabili se
#define CIRCIT_POWERUP_TIME 47000 

#define POWERUP_WAIT() bsp_DelayUS(CIRCIT_POWERUP_TIME);  //pauza da se upali napajenja kruga

//default values for 1st boot up
#define DEF_PERIOD  5*1000*1000     // [us] 5 seconds, frequency of taking samples
#define DEF_SPS     ADS1256_3750SPS // sps speed
#define DEF_NS      100             // number of samples


int z=0;

void config(unsigned int *k){
	FILE *f;
	f=fopen("/home/pi/smartsensor/adc_source/conf","rb");
	fread(k, sizeof(unsigned int), 3, f);
	k[2]=k[2]*1000;
	printf("%d %d %d",k[0],k[1],k[2]);
	fclose(f);
	return 0;
}

void sig_usr1(int signum, siginfo_t *info, void *ptr)
{
    config(conf);
	printf("signal uhvacen\n");
	z=1;

}

void catch_sigusr1()
{
    static struct sigaction _sigact;

    memset(&_sigact, 0, sizeof(_sigact));
    _sigact.sa_sigaction = sig_usr1;
    _sigact.sa_flags = SA_SIGINFO;

    sigaction(SIGUSR1, &_sigact, NULL);
}
/*
*********************************************************************************************************
*	name: main
*	function:  
*	parameter: NULL
*	The return value:  NULL
*********************************************************************************************************
*/


int  main()
{
    uint32_t id,i,j;
	int32_t *kanal1;
	int32_t *kanal2;
  	int32_t adc[8];
	int32_t volt[8];
	uint8_t ch_num;
	int32_t kanal[100];
	uint8_t buf[3];
	FILE *k1,*k2;
	uint32_t limit=conf[1]+1;
	uint32_t sleep=conf[2];
 
    clock_t start, end;
    double cpu_time_used;

	catch_sigusr1();

	kanal1=(int32_t *)malloc(sizeof(int32_t)*limit);
	kanal2=(int32_t *)malloc(sizeof(int32_t)*limit);

	if (!bcm2835_init())
        return 1;

    bcm2835_spi_begin();
    bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);   //default
    bcm2835_spi_setDataMode(BCM2835_SPI_MODE1);                //default
    bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_256);//default

    bcm2835_gpio_fsel(SPICS, BCM2835_GPIO_FSEL_OUTP);//
    bcm2835_gpio_write(SPICS, HIGH);
    bcm2835_gpio_fsel(DRDY, BCM2835_GPIO_FSEL_INPT);
    bcm2835_gpio_set_pud(DRDY, BCM2835_GPIO_PUD_UP);
    bcm2835_gpio_fsel(POWERPIN, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_write(POWERPIN,HIGH);
	bsp_DelayUS(47000);  //pauza da se upali napajenja kruga

   id = ADS1256_ReadChipID();
   printf("\r\n");
   printf("ID=\r\n");
	if (id != 3)
	{
		printf("Error, ASD1256 Chip ID = 0x%d\r\n", (int)id); return 1;
	}
	else
	{
		printf("Ok, ASD1256 Chip ID = 0x%d\r\n", (int)id);
	}
  	ADS1256_CfgADC(ADS1256_GAIN_1, conf[0]);
        ADS1256_StartScan(1);
	ch_num = 2;
	//if (ADS1256_Scan() == 0)
		//{
			//continue;
		//}


printf("this is\n");
while(1){
	printf("sparta1\n");
	if (z){
	limit=conf[1]+1;
	ADS1256_CfgADC(ADS1256_GAIN_1,conf[0]);
	sleep=conf[2];
	kanal1 = (int32_t *) realloc(kanal1, sizeof(int32_t)*(limit));
	kanal2 = (int32_t *) realloc(kanal2, sizeof(int32_t)*(limit));
	z=0;
}

	for(i=0;i<limit;i++){

		while(DRDY_IS_LOW());
		ADS1256_WriteReg(REG_MUX, 0x01);
		bsp_DelayUS(5);

		ADS1256_WriteCmd(CMD_SYNC);
                bsp_DelayUS(5);

                ADS1256_WriteCmd(CMD_WAKEUP);
                bsp_DelayUS(25);

		kanal2[i]=ADS1256_ReadData();
		while(!DRDY_IS_LOW());

		while(DRDY_IS_LOW());

		ADS1256_WriteReg(REG_MUX,0x23);
		bsp_DelayUS(5);
		ADS1256_WriteCmd(CMD_SYNC);
		bsp_DelayUS(5);
		ADS1256_WriteCmd(CMD_WAKEUP);
		bsp_DelayUS(25);

		kanal1[i]=ADS1256_ReadData();
		while(!DRDY_IS_LOW());

}
		bcm2835_gpio_write(POWERPIN,LOW); //ugasi napajanje

		printf("sparta2\n");

		k1=fopen("/home/pi/smartsensor/adc_source/kanal1","w+");
		k2=fopen("/home/pi/smartsensor/adc_source/kanal2","w+");
		for(i=0;i<limit-1;i++){ fprintf(k1,"%08ld;",kanal1[i+1]); fprintf(k2,"%08ld;",kanal2[i+1]); }
		fprintf(k1,"\n"); fprintf(k2,"\n");
		fclose(k1); fclose(k2);

		bsp_DelayUS(sleep);
		bcm2835_gpio_write(POWERPIN,HIGH); //upali napajanje
		bsp_DelayUS(47000);
	}

    bcm2835_spi_end();
    bcm2835_close();

    return 0;
}
