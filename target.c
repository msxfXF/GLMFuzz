// fuzz_target.c

#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Please provide an input file as argument\n");
        return 0;
    }

    FILE* file = fopen(argv[1], "rb");
    if (!file) {
        printf("Failed to open file\n");
        return 0;
    }

    char buffer[5];
    if (fread(buffer, 4, 1, file) != 1) {
        printf("Failed to read file\n");
        fclose(file);
        return 0;
    }
    buffer[4] = '\0';

    fclose(file);
    if (buffer[0] != 'A' || buffer[1] != 'B' || buffer[2] != 'C') {
        printf("Invalid input file\n");
        return 0;
    }
    if (strcmp(buffer, "FUZZ") == 0) {
        printf("Crash! Fuzzing triggered a problem!\n");
        buffer[10] = '\0';
        return EXIT_FAILURE;
    } else {
        printf("Success! The program ran as expected.\n");
    }
    if (strcmp(buffer, "FUzz") == 0) {
        printf("Crash!!\n");
        buffer[11] = '\0';
        return EXIT_FAILURE;
    }
    if (strcmp(buffer, "aazz") == 0) {
        printf("Crash 2!!\n");
        buffer[12] = '\0';
        return EXIT_FAILURE;
    }
}
