#include <stdio.h>
#include <stdlib.h> 
#include <time.h>
#include <math.h>

int main(void){
    FILE *fp;
    clock_t start, end;
    double cpu_time_used;
    int exp;
    int i,j,f4[10000];


    printf("writing test of data to file or SQLite db\n");

    printf("populating random data of integers\n");

    printf("Fields of 10, 100, 1000, 10000\n");

    for(i=0;i<10000;i++){
        f4[i]=rand();
    }

    for(i=0;i<4;i++){
        exp=pow(10,i+1);
        printf("writing to file %d number of integer sets\n", exp);
        start=clock();
        fp=fopen("testisfile","w+");
        for(j=0;j<exp;j++){
            fprintf(fp,"%08ld;",f4[j]);
        fprintf(fp,"\n");
        }
        fclose(fp);
        end=clock();
        cpu_time_used = (double)(end - start) / CLOCKS_PER_SEC;
        printf("time elapsed %f\n", cpu_time_used);
    }

    



    return 0;
}