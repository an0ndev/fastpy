#pragma once

#include <string>

namespace libfastpy::types {
    class String {
    public:
        std::string value;
        template <typename ...StdStringCtorArgs>
        String (StdStringCtorArgs ...stdStringCtorArgs) : value (stdStringCtorArgs...) {};
    };
    class Int {
    public:
        uintmax_t value;
        Int (uintmax_t const & initial) : value (initial) {};
        String __str__ () {
            return String (std::to_string (value));
        };
    };
};