float sin(float x){
    return ((x) / 1.0) - ((x*x*x) / 6.0) + ((x*x*x*x*x) / 120.0) - ((x*x*x*x*x*x*x) / 5040.0) + ((x*x*x*x*x*x*x*x*x) / 362880.0);
}

void main(){
    printf("sin(3.0f) = %f", sin(3.0f));
}