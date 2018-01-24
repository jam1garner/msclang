float someTestVariable;

int add1(int x)
{
    return x + 1;
}

void someBoringTest()
{
    int x = sizeof(int);
}

float sin(float x){
    return ((x) / 1.0) - ((x*x*x) / 6.0) + ((x*x*x*x*x) / 120.0) - ((x*x*x*x*x*x*x) / 5040.0);
}

int yetAnother_test_variable2;

void main(){
    int testVariable = 5;
    float otherVariable;

    int fun_ptr = &add1;
    (*fun_ptr)(10);

    otherVariable = 1.0f;
    testVariable = 0x3A;
    testVariable += 4;
    testVariable++;
    otherVariable = -otherVariable;
    otherVariable = (float)testVariable;
    int j = (3 + (int)otherVariable);

    goto testLabel;

    testLabel:

    j = NULL;
    j = M_E + M_PI;
    j = true;

    if( !(testVariable + 1 == 2) )
    {
        syscall_1(0);
    }
    else if (testVariable != 2)
    {
        syscall_1(4);
    }
    else
    {
        syscall_1(1);
    }
    //test test test
    do{
        break;
    }while(true);
    /*
    this
    code
    comment
    does
    nothing
    */
    if (fun_ptr==0){
        printf("oh no!\n");
    }

    for(int i=0;i<5;i++){
        switch(i)
        {
            case 0x0:
            case 0x1:
                testVariable += 1;
                break;
            case 0x2:
            case 0x3:
                testVariable += 2;
                break;
            default:
                return false;
                break;
        }
    }

    printf("testVariable = %i", testVariable); // "good comment"
}