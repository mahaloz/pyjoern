fn complete_job() {}
fn next_job() {}
fn refresh_jobs() {}
fn fast_unlock() {}
fn log_workers() {}

fn job_status(fast_job: i32) -> i32 {
    fast_job
}

fn schedule_job(needs_next: bool, fast_job: i32, mode: i32) -> i32 {
    if needs_next && fast_job != 0 {
        complete_job();
        if mode != 0 {
            next_job();
        }
    }

    refresh_jobs();
    if fast_job != 0 {
        fast_unlock();
    }

    complete_job();
    log_workers();
    job_status(fast_job)
}

fn main() {
    let argc: i32 = 2;
    if argc < 1 {
        println!("Invalid arg amount!");
        return;
    }

    if argc == 2 {
        println!("Two!");
    } else if argc == 4 {
        println!("Four!");
        schedule_job(argc != 0, argc + 1, argc + 2);
    } else {
        println!("Many!");
    }
}
