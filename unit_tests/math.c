void main(){
    //int math
    printf("2 + 2 = %i", 2+2);
    printf("2 * 2 = %i", 2*2);
    printf("2 / 2 = %i", 2/2);
    printf("2 - 2 = %i", 2-2);

    //float math
    printf("2f + 2f = %f", 2.0+2.0);
    printf("2f * 2f = %f", 2.0*2.0);
    printf("2f / 2f = %f", 2.0/2.0);
    printf("2f - 2f = %f", 2.0-2.0);

    //float math autocasting
    //float and int
    printf("2f + 2 = %f", 2.0 + 2);
    printf("2f * 2 = %f", 2.0 * 2);
    printf("2f / 2 = %f", 2.0 / 2);
    printf("2f - 2 = %f", 2.0 - 2);

    //int and float
    printf("2 + 2f = %f", 2 + 2.0);
    printf("2 * 2f = %f", 2 * 2.0);
    printf("2 / 2f = %f", 2 / 2.0);
    printf("2 - 2f = %f", 2 - 2.0);

    //Other
    printf("5 mod 2 = %i", 5 % 2);
    printf("-(2+3) = %i", -(2 + 3));
    printf("-(2f+3f) = %f", -(2.0 + 3.0));
}