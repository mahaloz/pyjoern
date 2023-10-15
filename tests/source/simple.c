int main(int argc, char** argv) {
    if (argc < 1 ) {
        puts("Invalid arg amount!");
        return -1;
    }

    if (argc == 2) {
        puts("Two!");
    }
    else if (argc == 4)
        puts("Four!");
    }
    else {
        puts("Many!");
    }

    return 0;
}