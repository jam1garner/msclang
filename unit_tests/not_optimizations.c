void main(){
    //This should be optimized down to if and != instead of a not, an == and an if
    int c = !( 3+4 == 8 );
    if(c){
        printf("Success");
    }

    //This should be optimized down to ifNot instead of if and not
    if(!true){
        printf("Success");
    }

    //This should be optimized down to if and <= instead of if, not and >
    c = !(3 > 4);
    if(c){
        printf("Success");
    }
}