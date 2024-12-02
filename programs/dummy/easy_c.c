#include <stdio.h>
#include <math.h>



double degrees_to_radians(double degrees) { 
    return degrees / 180.0 * M_PI; 
} 

int main() {
    int angle = 0;
    printf("Give me an angle: ");
    scanf("%d", &angle);

    double number = cos(degrees_to_radians(angle));
    // double number = cos((angle));
    printf("%f\n", number);

    return 0;
}