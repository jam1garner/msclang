void test(){
    printf("test");
}

void main(){
    int t = test;
    (*t)();
}
