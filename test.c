float someTestVariable;

int add1(int x)
{
    return x + 1;
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

    j = NULL;
    j = M_E + M_PI;
    j = true;

    if( !(testVariable + 1 == 2) ){
        syscall_1(0);
    }
    else{
        syscall_1(1);
    }
    //test test test
    while(true){
        break;
    }
    /*
    this
    code
    comment
    does
    nothing
    */

    for(int i=0;i<5;i++){
        return false;

    }

    printf("testVariable = %i", testVariable); // "good comment"
}