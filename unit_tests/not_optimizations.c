void main(){
    //This should be optimized down to if and != instead of a not, an == and an if
    if(!(3 + 4 == 8)){
        printf("Success");
    }

    //This should be optimized down to ifNot instead of if and not
    if(!true){
        printf("Success");
    }

    //This should be optimized down to if and <= instead of if, not and >
    if(!(3 > 4)){
        printf("Success");
    }
}