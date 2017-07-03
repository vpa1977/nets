
#include "rxcpp/rx.hpp"
// create alias' to simplify code
// these are owned by the user so that
// conflicts can be managed by the user.
namespace rx=rxcpp;
namespace rxsub=rxcpp::subjects;
namespace rxu=rxcpp::util;

#include <cctype>
#include <clocale>
#include <windows.h>
// At this time, RxCpp will fail to compile if the contents
// of the std namespace are merged into the global namespace
// DO NOT USE: 'using namespace std;'

void SamplePublish()
{
    // sample 1
    {
        auto keys = rx::observable<>::create<int>(
            [](rx::subscriber<int> dest) {
            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        });
        keys.subscribe([](int val) {
            std::cout << val << std::endl;
        });
        std::cout << "done " << std::endl;
    }
    // connectable
    {
        auto keys = rx::observable<>::create<int>(
            [](rx::subscriber<int> dest) {
            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        }).publish();
        keys.subscribe([](int val) {
            std::cout << val << std::endl;
        });
        std::cout << "done " << std::endl;
        keys.connect();
    }

    // refcount
    {
        auto keys = rx::observable<>::create<int>(
            [](rx::subscriber<int> dest) {
            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        }).publish();
        keys.subscribe([](int val) {
            std::cout << val << std::endl;
        });

        std::cout << "before refcount " << std::endl;
        keys.ref_count().subscribe([](int val) {
            std::cout << val << std::endl;
        });
        std::cout << "before connectable " << std::endl;
        keys.connect();
    }
}


void Subject()
{
    // subject - hot 
    {
        std::cout << "subjects " << std::endl;
        rx::subjects::subject<int> subj;
        auto keys = rx::observable<>::create<int>(
            [](rx::subscriber<int> dest) {
            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        });

        subj.get_observable().
            subscribe(
                [](int val) {
            std::cout << "subject emits " << val << std::endl;
        }
        );

        keys.subscribe(subj.get_subscriber());

    }
}

void BackPressure()
{
    // debounce
    {
        auto keys = rx::observable<>::create<int>(
            [](rx::subscriber<int> dest) {
            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        });
        keys.debounce(std::chrono::seconds(1)).subscribe([](int val) {
            std::cout << "debounce " << val << std::endl;
        });
        std::cout << "done " << std::endl;
    }

    // buffer
    {
        auto keys = rx::observable<>::create<int>(
            [](rx::subscriber<int> dest) {
            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        });
        keys.buffer(3).subscribe(
            [=](const std::vector<int>& x)
        {
            for (auto v : x)
                std::cout << v << " ";
            std::cout << std::endl;

        }
        );
        std::cout << "done " << std::endl;
    }
}

void Threading()
{
    // scheduler
    // subscribe on -> Subscriber thread, observe_on -> Subscription thread (new one!)
    {
        std::cout << " Current thread:" << GetCurrentThreadId() << std::endl;
        auto keys = rx::observable<>::create<int>(
            [=](rx::subscriber<int> dest) {
            std::cout << " Subscriber thread:" << GetCurrentThreadId() << std::endl;

            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        }).subscribe_on(rx::identity_current_thread()).
            observe_on(rx::observe_on_new_thread());
        keys.subscribe( // thread 1
            [=](int)
        {
            std::cout << " Subscription thread:" << GetCurrentThreadId() << std::endl;
        });

        auto next = keys.map([=](int val) // thread 2
        {
            std::cout << " map thread:" << GetCurrentThreadId() << std::endl;
            return val;
        });
        next.subscribe([](int)
        {
            std::cout << " Subscription thread2:" << GetCurrentThreadId() << std::endl;
        });
        next.as_blocking();
    }
    
    std::cout << std::endl << std::endl;
    // reuse same thread
    {
        std::cout << " Current thread:" << GetCurrentThreadId() << std::endl;
        // rather ugly way to force execution on a single thread
        auto otherThread = rxcpp::observe_on_one_worker(
            rx::observe_on_new_thread()
            .create_coordinator()
            .get_scheduler());


        auto keys = rx::observable<>::create<int>(
            [=](rx::subscriber<int> dest) {
            std::cout << " Subscriber thread:" << GetCurrentThreadId() << std::endl;

            dest.on_next(1);
            dest.on_next(2);
            dest.on_next(3);
            dest.on_completed();
        }).subscribe_on(rx::identity_current_thread()).
            observe_on(otherThread);

        keys.subscribe( // thread 1
            [=](int)
        {
            std::cout << " Subscription thread:" << GetCurrentThreadId() << std::endl;
        });

        auto next = keys.map([=](int val) // thread 2
        {
            std::cout << " map thread:" << GetCurrentThreadId() << std::endl;
            return val;
        }).as_blocking();
        next.subscribe([](int)
        {
            std::cout << " Subscription thread2:" << GetCurrentThreadId() << std::endl;
        });
    }
}

void Errors()
{
    // unhandled exception
    auto keys = rx::observable<>::create<int>(
        [=](rx::subscriber<int> dest) {
        dest.on_next(1);
        dest.on_next(2);
        dest.on_next(3);
        dest.on_completed();
    }) | rx::operators::map([=](int) { // first operator throws
        if (true)
            throw std::exception("oops");
        return 0;
    });

    keys.subscribe([=](int) {
        std::cout << "subscription1 called" << std::endl;
    }, [=](std::exception_ptr err)
    {
        try {
            if (err) {
                std::rethrow_exception(err);
            }
        }
        catch (const std::exception& e) {
            std::cout << "Caught exception in subscription1 \"" << e.what() << "\"\n";
        }
    });
    
    auto next = keys | rx::operators::map([=](int) { return 0; }); // second ok
    next.subscribe([=](int) {
        std::cout << "subscription2 called" << std::endl;
    }, [=](std::exception_ptr err)
    {
        try {
            if (err) {
                std::rethrow_exception(err);
            }
        }
        catch (const std::exception& e) {
            std::cout << "Caught exception in subscription2 \"" << e.what() << "\"\n";
        }
    });

}

int main()
{
    Errors();
    return 0;
}
