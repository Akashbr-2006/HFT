#include<stdio.h>
int mian(){
    int num,i;
    printf("Enter the number: ");
    scanf("%d",&num);
    printf("multiplication table of %d is: \n",num);
    for(i=1;i<=10;i++){
        printf("%d * %d = %d\n",num,i,num*i);
    }
    return 0;
}