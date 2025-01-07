int schedule_job(int needs_next, int fast_job, int mode)
{
    if (needs_next && fast_job) {
        complete_job();
        if (mode == EARLY_EXIT)
            goto cleanup;

        next_job();
    }

    refresh_jobs();
    if (fast_job != 0)
        fast_unlock();

cleanup:
    complete_job();
    log_workers();
    return job_status(fast_job);
}

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
        schedule_job(argc, argc+1, argc+2);
    }
    else {
        puts("Many!");
    }

    return 0;
}
